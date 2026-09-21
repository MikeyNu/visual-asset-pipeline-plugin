# Transfer, repository safety, and Desktop Commander

## Distinguish environments

The chat sandbox, a GitHub repository, and a Windows desktop are separate filesystems. `sandbox:/mnt/data/file.png` is a chat artifact link, not a public URL that PowerShell can download. A generated path under `/mnt/data` does not exist at `C:\mnt\data` on the user's device.

Before writes inspect the exact root, current branch, working tree, relevant asset directory, permissions, existing consumer code, and project workflow. Use the real deployment base path and filename case. Never operate on a similarly named nested root without checking it.

A project can be local-only. For example, the user has previously identified a Biocor checkout at `C:\Users\USER\Desktop\biocor-global\biocor-global`; this is contextual guidance, not proof it exists in a future run. Inspect it when that project is actually the target. Do not hard-code it into generic commands or create a remote automatically.

## Preferred transfer order

1. Use a genuine shared mount or documented binary/file-reference transfer when one exists.
2. For an authorized Git-based workflow, write the assets in the checkout, commit them with their consuming code, push only when permitted, and synchronize the destination using the established workflow.
3. Use an authorized, actually reachable HTTPS artifact or signed download route. Never publish private assets merely to obtain a public URL.
4. When only text transport exists, transfer a programmatically encoded, checksummed envelope in bounded chunks and decode it on the destination. This is a fallback for modest files, not an excuse to paste megabytes into chat or exceed tool limits.
5. If no reliable route exists, leave transfer blocked and name the required capability or input. Do not invent a URL or call a text API binary-capable.

## Desktop Commander workflow

Discover the available tool descriptions. In the inspected connector schema, `list_directory`, `read_file`, `read_multiple_files`, `get_file_info`, `start_process`, and `read_process_output` are separate capabilities. `write_file` accepts text content and has a documented chunking convention, so it must not be assumed to accept arbitrary image bytes or a sandbox link.

Inspect the destination with directory/file tools. Use terminal/process tools for native hashing, decoding, tests, and the project's existing `devctl` entry point where present. Group independent inspections into a small number of meaningful operations, respecting permissions and the connector's current limits. Do not change quotas, allowed-directory restrictions, or connector configuration to make transfer possible.

If text-only transport is necessary:
1. Run `assetctl.py pack` in the environment containing the real files. It produces base64 derived by code and reports the bundle SHA-256.
2. Move the helper and envelope through a supported route. For `write_file`, follow its current 25-30-line chunk limit, with explicit rewrite/append semantics. Use bounded line lengths as well. Never pass base64 into a connector argument explicitly designated as a file reference.
3. Keep the envelope in a staging folder, not the production image folder. Do not log sensitive prompts or URLs with it.
4. Run `assetctl.py receive` with the intended root, allowed relative asset prefix, and expected bundle SHA-256. It defaults to dry-run. Inspect the plan, then add `--apply` for the requested write.
5. Re-run verification at the destination and inspect the image through a supported viewer.
6. Update consumer code using ordinary project conventions. Run CI and rendered QA locally.

A successful envelope write is not evidence that the binary image has been decoded into its production path. The receiver is create-only: a different existing file is a conflict; an identical file is an idempotent no-op. Prefer new content-hashed filenames for replacements and then update imports.

## GitHub workflow

Inspect the specific repository, branch, and file contents through available connected tools before changes. Prefer authenticated Git in an actual checkout for multi-file code plus binary updates, when available and authorized. A text-only push tool is not sufficient for arbitrary raster bytes.

GitHub's REST Contents API accepts base64 file content and requires the current blob SHA for updates [R10]. Use it only through a verified, authorized API route; never assume a particular connector exposes the same schema. Serialize conflicting file updates. Preserve the chosen branch and scope.

Do not confuse the Git blob SHA with the asset's SHA-256. They serve different purposes. Verify remote bytes or retrieve the actual committed file when practical, then verify local synchronization. An LFS pointer is not the image; ensure the intended build/runtime fetches the actual object before claiming success.

For the user's established remote-first/local-CI workflow, include binaries in the same candidate revision as consumers, push when authorized, then use Desktop Commander to pull the exact revision and run the existing CI workflow. For a local-only project, edit the inspected local working tree instead. Do not silently replace either workflow.

## Safety and integrity

Keep private references, prompts, transfer envelopes, and raw receipts out of public asset directories. A minimal public runtime manifest may contain IDs, URLs, dimensions, and alt information; full prompt and provenance records belong in a non-public project location subject to project policy.

Reject absolute or escaping archive paths, `..`, Windows drive/UNC paths, reserved device names, alternate data streams, duplicate case-folded paths, symlinks, and junctions in the destination chain. Verify byte lengths, expected hashes, decoding, and allowed file types. The included receiver preflights a batch and installs each file atomically, but does not claim a multi-file database transaction. Coordinate against concurrent writers; no helper defeats a hostile process that controls the destination filesystem.

Do not reset, clean, stash, force-push, rewrite history, or delete unrelated assets. Report a dirty tree; do not assume every existing change is yours. Version new files and update consumers surgically. Delete stale assets only after checking references and receiving the relevant authorization.
