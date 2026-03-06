# Changelog

This file tracks notable changes for the `py_aurora_remote` repository.

## 2.1.1

### Added

- Added full Python coverage for the public Aurora Remote SDK 2.1.1 feature set, including:
  - session creation flags and listener-backed session creation
  - standalone `TimeSyncClient`
  - pose covariance retrieval and readable conversion
  - pose augmentation APIs
  - persistent config APIs
  - transform manager APIs
  - camera mask APIs
  - dashcam recorder APIs
  - controller power-operation APIs
- Added new 2.1.1 example scripts:
  - `time_sync.py`
  - `wallclock_sync.py`
  - `pose_augmentation.py`
  - `pose_covariance.py`
  - `persistent_config.py`
  - `transform_manager.py`
  - `camera_mask.py`
  - `dashcam_recorder.py`
  - `system_power.py`
- Added a unified source file header across Python sources with project, file, and copyright information.

### Changed

- Updated the exported Python package surface and version metadata to align with Aurora Remote SDK `2.1.1`.
- Updated top-level English and Chinese READMEs and regenerated the API documentation under `docs/`.
- Updated explicit manual example IP defaults to `192.168.11.1` while keeping auto-discovery defaults unchanged.

### Fixed

- Fixed discovery-based standalone example address selection in `examples/_demo_common.py` to prefer usable IPv4 addresses over IPv6 link-local addresses without a scope ID.
- Fixed `nan` position reporting in `examples/pose_augmentation.py` by removing the low-rate-mode override and snapshotting pose tuples in the callback.
- Fixed stride-aware decoding for image, depth, point3D, and segmentation buffers in the Python SDK.
- Fixed RGB/BGR handling and camera-coordinate rendering issues in `examples/dense_point_cloud.py`.
- Fixed segmentation map stride handling in the Python SDK and semantic segmentation demo path.

## Earlier History

- Native Aurora Remote SDK release history is tracked in `cpp_sdk/Changelog.md`.
- Earlier Python repository changes prior to the 2.1.1 parity update are tracked in git history and the project README files.
