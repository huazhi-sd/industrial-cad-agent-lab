# Onshape Import And Replace Workflow

This reference describes the safe sequence for uploading a generated spring STEP and replacing a faulty imported spring instance in an Onshape assembly.

## Safety Rules

- Never hard-code API keys or secrets.
- Read credentials from environment variables:
  - `ONSHAPE_ACCESS_KEY`
  - `ONSHAPE_SECRET_KEY`
- Use `allowFaultyParts=false` during import when the goal is clean replacement geometry.
- Store old instance ids and transforms before editing an assembly.

## Import Parameters

Use the blob element upload endpoint for STEP import:

```text
POST /api/v6/blobelements/d/{documentId}/w/{workspaceId}
```

Use these multipart form defaults:

```text
storeInDocument=true
allowFaultyParts=false
flattenAssemblies=false
formatName=STEP
```

After import, verify:

```text
bodyType = solid
isMesh = false
```

## Replacement Sequence

1. Find the old assembly instance.
2. Save:
   - old instance id,
   - old element id,
   - old part id,
   - transform matrix.
3. Upload and import the new STEP.
4. Insert the new part into the same assembly.
5. Apply the saved transform.
6. Visually check the overlay.
7. Delete the old faulty instance only after the new one is positioned correctly.

## Rollback

If replacement is wrong, delete the new instance and keep the old instance. If the old instance was already deleted, reinsert it using the saved element id, part id, and transform.
