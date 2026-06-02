# Motherboard Tray + Board Datum V1

This layer mounts a simplified mATX motherboard datum onto `motherboard_tray_v1`.

## Scope

- Top-level part 1: motherboard tray with integrated standoffs.
- Top-level part 2: mATX motherboard datum.
- Board datum includes:
  - 8 standard mATX mounting holes;
  - rear I/O envelope;
  - simplified I/O armor;
  - first PCIe x16 slot datum;
  - dual EPS 8-pin envelopes;
  - 24-pin ATX envelope.

## Design Policy

This file is for chassis layout and clearance checks. It is not a cosmetic
motherboard model. CPU, DIMM, SSD, chipset, VRM, and connector detail should
only be added later if they are needed for a specific case clearance decision.

## Validation

Run:

```powershell
python validate_motherboard_tray_board_v1.py
```

Expected gates:

- no mirror/scale-like CAD operations;
- tray and board share the same 8-hole mATX pattern;
- motherboard back face sits on the standoff tips;
- assembly has exactly 2 top-level parts;
- rear I/O is low X;
- PCIe is lower Z;
- 24-pin is high X.
