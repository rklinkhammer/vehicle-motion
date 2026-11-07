# Repository boundaries

This repository owns autonomous vehicle behavior, planning contracts and offline
simulation. dmotor owns controller/runtime/driver and protection firmware.
All eventual daemon access MUST use dmotor_client (`dmotor::client`); never copy
socket/protocol code or access controller devices directly. No automatic arm,
prepare, enable, reconnect, replay or mission resume.
Hardware testing is paused pending assembled monitor and motor boards. Do not
change dmotor's commissioning-first release scope or claim live recovery exists.
Simulation constants are fictional, not commissioned limits or geometry.
Read docs/architecture.md and docs/decisions.md before adding runtime integration.
Use Python standard library for the offline prototype; planned PS integration is
C++14, consistent with dmotor. Run `python3 -m unittest discover -s tests -v`.
