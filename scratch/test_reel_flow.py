import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Login
login_data = json.dumps({'username': 'admin@hiramoti.com', 'password': 'Hiramoti@1987'}).encode('utf-8')
req = urllib.request.Request('http://127.0.0.1:5000/api/admin/login', data=login_data, headers={'Content-Type': 'application/json'})
res = urllib.request.urlopen(req)
token = json.loads(res.read().decode('utf-8'))['token']
print('1. Logged in, token obtained.')

# 2. Upload cover image
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body = (
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="file"; filename="qa_custom_cover.jpg"\r\n'
    f'Content-Type: image/jpeg\r\n\r\n'
    f'fake_jpg_binary_content_qa_audit_1234567890\r\n'
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="media_type"\r\n\r\n'
    f'image\r\n'
    f'--{boundary}--\r\n'
).encode('utf-8')

req = urllib.request.Request('http://127.0.0.1:5000/api/admin/upload-media', data=body, headers={
    'Content-Type': f'multipart/form-data; boundary={boundary}',
    'Authorization': f'Bearer {token}'
})
res = urllib.request.urlopen(req)
upload_res = json.loads(res.read().decode('utf-8'))
print('2. Upload response:', upload_res)
uploaded_img = upload_res['url']
assert uploaded_img.startswith('assets/uploads/'), 'Uploaded path must start with assets/uploads/'

# 3. Create reel
reel_payload = json.dumps({
    'title': 'QA Custom Cover Test Reel',
    'url': 'https://www.instagram.com/reel/TESTCOVER123/',
    'image': uploaded_img,
    'price': '₹999',
    'offer': 'TEST OFFER'
}).encode('utf-8')
req = urllib.request.Request('http://127.0.0.1:5000/api/admin/reels', data=reel_payload, headers={
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
})
res = urllib.request.urlopen(req)
create_res = json.loads(res.read().decode('utf-8'))
print('3. Create reel response:', create_res)
reel_id = create_res['reel']['id']
assert create_res['reel']['image'] == uploaded_img, 'Saved image must match uploaded image!'

# 4. Fetch reel from admin API
req = urllib.request.Request('http://127.0.0.1:5000/api/admin/reels', headers={'Authorization': f'Bearer {token}'})
res = urllib.request.urlopen(req)
all_reels = json.loads(res.read().decode('utf-8'))['reels']
found = [r for r in all_reels if r['id'] == reel_id][0]
print('4. Retrieved reel image from DB:', found['image'])
assert found['image'] == uploaded_img, 'DB image does not match!'

# 5. Fetch reel from public API
req = urllib.request.Request('http://127.0.0.1:5000/api/reels')
res = urllib.request.urlopen(req)
public_reels = json.loads(res.read().decode('utf-8'))['reels']
pub_found = [r for r in public_reels if r['id'] == reel_id][0]
print('5. Retrieved reel from public API:', pub_found['image'])
assert pub_found['image'] == uploaded_img, 'Public API image does not match!'

# 6. Verify image file is actually accessible via HTTP GET
req = urllib.request.Request(f'http://127.0.0.1:5000/{uploaded_img}')
res = urllib.request.urlopen(req)
assert res.status == 200, f'HTTP status {res.status}'
print(f'6. Image served successfully over HTTP 200 ({len(res.read())} bytes)')

# 7. Clean up test reel
req = urllib.request.Request(f'http://127.0.0.1:5000/api/admin/reels/{reel_id}', headers={'Authorization': f'Bearer {token}'}, method='DELETE')
urllib.request.urlopen(req)
print('7. Test reel deleted and cleaned up successfully!')
print('ALL BACKEND AUDIT CHECKS PASSED!')
