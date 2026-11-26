# Rope Skipping Counter – WebRTC diagnostics update

This update improves WebRTC connection diagnostics and adds optional TURN server support.

## Deploy
1. Replace the files in the GitHub repository with this ZIP's contents.
2. Commit and push the changes.
3. In Render, choose **Manual Deploy → Deploy latest commit**.
4. Open `/camera`, create a new pairing QR code, and scan it again. Do not reuse an old QR code.

## TURN configuration (recommended if the screen remains black)
The app still works with the public Google STUN server, but STUN alone cannot guarantee a connection across all mobile carriers, Wi-Fi routers, and NAT/firewall configurations.

Create a TURN service with a provider and add these environment variables in Render:
- `TURN_URLS`: comma-separated TURN URLs supplied by the provider, e.g. `turn:host:3478?transport=udp,turns:host:5349?transport=tcp`
- `TURN_USERNAME`: provider-issued username
- `TURN_CREDENTIAL`: provider-issued credential/password

Do not put TURN credentials in source code or share them publicly. After setting these variables, redeploy and create a fresh QR pairing.

## What changed
- PC and phone use the same configured ICE server list.
- Optional TURN configuration is read from Render environment variables.
- PC and phone show WebRTC connection state and log ICE state to the browser console.
- Remote video uses a fallback MediaStream when the browser does not populate `event.streams`.
- Signaling polling avoids overlapping requests and surfaces HTTP/signaling errors.

## Important
A QR pairing only proves that the phone opened the pairing page. The actual video path is WebRTC. A successful end-to-end test requires the phone's WebRTC connection state to become `connected` and the PC to receive a video track. This ZIP has not been tested against your live Render instance or physical phone/network; verify after deployment.
