# Motherboard Tray V1

This is the first clean restart point for the mATX case project.

## Scope

- One mATX motherboard tray datum part.
- 1.0 mm tray plate.
- 8 integrated mATX standoffs.
- M3 clearance holes through the standoffs.
- Raised board-envelope markers on the tray back side.
- Low-X rear I/O side marker to protect handedness.

## Not Included Yet

- Rear PCIe slot bracket panel.
- PSU chamber.
- HDD mount.
- fan mounts.
- side/top/front case panels.
- cosmetic motherboard details.

## Coordinate Contract

- X: rear I/O side to front side of motherboard.
- Y: tray normal. Negative Y is motherboard/component side.
- Z: lower PCIe side to upper CPU power side.
- Origin: lower rear corner of the motherboard PCB envelope.

## Validation

Run:

```powershell
python validate_motherboard_tray_v1.py
```

Expected gates:

- exactly 8 mATX support locations: B, C, F, R, H, J, L, M;
- no mirror/scale-like CAD operations;
- tray envelope equals `253.84 x 253.84 mm`;
- standoffs extend to `Y=-6.5 mm`;
- rear I/O side marker remains on low X.
