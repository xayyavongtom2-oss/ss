# Rope Skipping Counter

ເວັບນັບການກະໂດດເຊືອກດ້ວຍ AI Pose Tracking ມີ Login/Register, ປະຫວັດ, ສະຖິຕິ ແລະ Leaderboard ຮ່ວມກັນຜ່ານຖານຂໍ້ມູນ.

## ວິທີເປີດໃນ Windows

1. ຕິດຕັ້ງ Python 3.10 ຫຼືໃໝ່ກວ່າ.
2. Extract ZIP ແລ້ວເປີດ Folder ໃນ VS Code.
3. ເປີດ Terminal ແລ້ວພິມ:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

4. ເປີດ http://127.0.0.1:5000
5. ສ້າງບັນຊີ ແລ້ວກົດເລີ່ມຝຶກ.

## ການໃຊ້ກ້ອງ

- Browser ຈະຂໍສິດໃຊ້ Camera, ກົດ Allow.
- ຕ້ອງວາງໂທລະສັບ/ຄອມໃຫ້ເຫັນຮ່າງກາຍຕັ້ງແຕ່ຫົວຮອດຕີນ.
- ການນັບໃຊ້ MediaPipe Pose ຜ່ານ CDN; ຕ້ອງມີ Internet.
- ການນັບໃຊ້ການຂຶ້ນ-ລົງຂອງລຳຕົວເປັນ heuristic. ຄວາມແມ່ນຍຳອາດຂຶ້ນກັບມຸມກ້ອງ, ແສງ, ແລະທ່າກະໂດດ; ຄວນທົດສອບກ່ອນໃຊ້ແຂ່ງຂັນ.
- ກ້ອງໃນ browser ຕ້ອງໃຊ້ localhost ຫຼື HTTPS. ຖ້າ deploy online ຕ້ອງເປີດ HTTPS.

## Deploy ຂຶ້ນອອນລາຍດ້ວຍ Render

1. ອັບໂຫຼດ project ນີ້ໄປ GitHub.
2. ເຂົ້າ Render ແລ້ວສ້າງ Blueprint ຈາກ repository.
3. `render.yaml` ຈະສ້າງ Web Service ແລະ PostgreSQL database.
4. ກວດໃຫ້ມີ `SECRET_KEY` ແລະ `DATABASE_URL` ໃນ Environment.
5. ເມື່ອ deploy ສຳເລັດ ເປີດ URL HTTPS ແລ້ວທົດສອບກ້ອງ.

## ໝາຍເຫດ
- ລະຫັດຜ່ານຖືກ hash ກ່ອນບັນທຶກ.
- Leaderboard ຄິດຈາກຜົນການຝຶກທີ່ກົດ Stop ແລະບັນທຶກສຳເລັດ.
- ຄ່າ Calories ເປັນການປະເມີນຄ່າຄົງທີ່ຕໍ່ການກະໂດດ ບໍ່ແມ່ນການວັດທາງການແພດ.


## ໃຊ້ກ້ອງມືຖື ແຕ່ປະມວນຜົນໃນ PC

1. Deploy ເວັບໃຫ້ໄດ້ HTTPS (ຕົວຢ່າງ Render).
2. Login ໃນ PC ແລ້ວເຂົ້າໜ້າ Camera.
3. ກົດ “ສ້າງ QR Code ເພື່ອເຊື່ອມຕໍ່”.
4. ໃຊ້ກ້ອງມືຖືສະແກນ QR ແລ້ວກົດອະນຸຍາດ Camera.
5. ວາງມືຖືໃຫ້ເຫັນຮ່າງກາຍເຕັມຕົວ. ພາບສົດຈະປາກົດໃນ PC ແລະ AI ເຮັດວຽກໃນ PC browser.

ການສົ່ງພາບໃຊ້ WebRTC ແລະ STUN server. ການເຊື່ອມຕໍ່ຜ່ານບາງເຄືອຂ່າຍອາດຕ້ອງມີ TURN server ເພີ່ມ. ລະຫັດຈັບຄູ່ຖືກເກັບໃນ memory ຂອງ server ແລະມີອາຍຸ 1 ຊົ່ວໂມງ; ສຳລັບການໃຊ້ production ຫຼາຍ instance ຄວນຍ້າຍ signaling ໄປ Redis.


### Render dependency fix
The PostgreSQL driver is pinned to `psycopg[binary]==3.3.9` and the SQLAlchemy URL uses `postgresql+psycopg://` so it loads psycopg 3 rather than the psycopg2 driver.


## ການແກ້ໄຂ QR Code (FIX)
- ເພີ່ມ `import secrets` ໃນ `app.py` ເພື່ອໃຫ້ endpoint `/api/pair` ສ້າງ pairing code ໄດ້.
- ເພີ່ມ ProxyFix ເພື່ອສ້າງ URL HTTPS ທີ່ຖືກຕ້ອງຫຼັງ Render proxy.
- ເພີ່ມການສະແດງ error ແລະລິ້ງເຂົ້າມືຖືສຳຮອງ ຖ້າ QR library ໂຫຼດບໍ່ສຳເລັດ.
