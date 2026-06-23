# migrate_to_v2.py
import json, os, base64
from datetime import datetime
# This is a minimal migration helper - tailor to your old file layout
OLD = "secure_notes.json"
NEW = "secure_notes_v2.json"
if not os.path.exists(OLD):
    print("No old file found.")
    exit(0)
with open(OLD,'r') as f:
    old = json.load(f)
new = {}
for title, meta in old.items():
    # assume meta['content'] held encrypted object; we cannot re-encrypt without password
    # This script only wraps old ciphertext under a single version object so data isn't lost
    version_id = "migrated-" + base64.b64encode(title.encode()).decode()
    # store the old blob (complete) into ciphertext field so user can run manual migrate if needed
    new[title] = {'note_id':title, 'versions':[{'version_id':version_id,'ciphertext':base64.b64encode(json.dumps(meta).encode()).decode(),'nonce':'','ts':datetime.now().isoformat()}], 'current':version_id}
with open(NEW,'w') as f:
    json.dump(new,f)
print("Migration wrapper created:", NEW)
