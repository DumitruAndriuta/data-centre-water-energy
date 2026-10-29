"""Minimal SigV4 client for the MSD-LIVE public S3 access points (anonymous credentials from
/api/get-aws-credentials). Used to fetch the IM3 data centre atlas.

    python im3_s3.py p147s-4h760 list p147s-4h760/
    python im3_s3.py p147s-4h760 get <key> <dest>
"""
import datetime, hashlib, hmac, json, sys, urllib.parse, urllib.request


def creds():
    return json.load(urllib.request.urlopen("https://data.msdlive.org/api/get-aws-credentials"))


def _sign(k, m):
    return hmac.new(k, m.encode(), hashlib.sha256).digest()


def _req(c, host, path, query, out=None):
    cr, region = c["credentials"], c["region"]
    t = datetime.datetime.now(datetime.timezone.utc)
    amz, d = t.strftime("%Y%m%dT%H%M%SZ"), t.strftime("%Y%m%d")
    qs = "&".join(f"{urllib.parse.quote(k, safe='-_.~')}={urllib.parse.quote(v, safe='-_.~')}" for k, v in sorted(query.items()))
    ph = "UNSIGNED-PAYLOAD"
    hdrs = {"host": host, "x-amz-content-sha256": ph, "x-amz-date": amz, "x-amz-security-token": cr["sessionToken"]}
    sh = ";".join(sorted(hdrs))
    ch = "".join(f"{k}:{hdrs[k]}\n" for k in sorted(hdrs))
    canon = "\n".join(["GET", urllib.parse.quote(path, safe="/-_.~"), qs, ch, sh, ph])
    scope = f"{d}/{region}/s3/aws4_request"
    sts = "\n".join(["AWS4-HMAC-SHA256", amz, scope, hashlib.sha256(canon.encode()).hexdigest()])
    k = _sign(_sign(_sign(_sign(("AWS4" + cr["secretKey"]).encode(), d), region), "s3"), "aws4_request")
    sig = hmac.new(k, sts.encode(), hashlib.sha256).hexdigest()
    hdrs["Authorization"] = f"AWS4-HMAC-SHA256 Credential={cr['accessKeyId']}/{scope}, SignedHeaders={sh}, Signature={sig}"
    url = f"https://{host}{urllib.parse.quote(path, safe='/-_.~')}" + ("?" + qs if qs else "")
    r = urllib.request.urlopen(urllib.request.Request(url, headers={k: v for k, v in hdrs.items() if k != "host"}))
    if out:
        with open(out, "wb") as f:
            while b := r.read(1 << 20):
                f.write(b)
        return out
    return r.read().decode()


def _host(c, access_point):
    return f"{access_point}-{c['accountId']}.s3-accesspoint.{c['region']}.amazonaws.com"


def get(access_point, key, dest):
    c = creds()
    return _req(c, _host(c, access_point), "/" + key, {}, out=dest)


if __name__ == "__main__":
    c = creds()
    host = _host(c, sys.argv[1])
    if sys.argv[2] == "list":
        print(_req(c, host, "/", {"list-type": "2", "prefix": sys.argv[3]}))
    else:
        print(_req(c, host, "/" + sys.argv[3], {}, out=sys.argv[4]))
