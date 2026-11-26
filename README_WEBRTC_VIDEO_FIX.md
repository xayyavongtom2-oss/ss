# Rope Skipping Counter – WebRTC Video Track Fix

## Critical fix
The PC creates the WebRTC offer and receives the phone camera stream. The previous code created an offer without first reserving a video transceiver, so the SDP offer could contain no `m=video` media section. In that case the phone could send an Answer successfully while no remote video track was negotiated, leaving the PC preview black.

The updated `templates/camera.html` calls `pc.addTransceiver("video", {direction: "recvonly"})` before `createOffer()` and checks that the generated SDP contains `m=video`. It also adds visible connection/ICE state diagnostics and remote video playback logging.

## Deploy
1. Replace the GitHub repository files with the contents of this ZIP.
2. Commit and push the changes.
3. In Render, run **Manual Deploy → Deploy latest commit**.
4. Open `/camera`, create a NEW QR code, and scan it. Do not reuse an old pairing.
5. Keep the phone page open and the camera running.

## If it still does not connect
If the PC shows `ICE: failed` or WebRTC `failed`, configure a TURN service in Render using `TURN_URLS`, `TURN_USERNAME`, and `TURN_CREDENTIAL`. STUN alone cannot guarantee connectivity across all networks. Do not share TURN credentials publicly.

If the PC shows `ICE: connected` but the preview remains black, open the PC browser developer console (F12 → Console) and check for `PC received remote track` and `Remote video is PLAYING`.

This patch fixes the missing video transceiver in the source. It has not been tested against the user's live Render deployment or physical devices; a live end-to-end test is still required.
