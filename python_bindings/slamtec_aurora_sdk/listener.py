# /*
#  *  SLAMTEC Aurora
#  *  Copyright 2013 - 2025 SLAMTEC Co., Ltd.
#  *
#  *  http://www.slamtec.com
#  *
#  *  Aurora Remote SDK Python
#  *  File: python_bindings/slamtec_aurora_sdk/listener.py
#  *
#  */
"""
Aurora SDK listener bridge.

This module exposes a Python listener base class that mirrors the native
slamtec_aurora_sdk_listener_t callback surface.
"""

import ctypes
import traceback

from .data_types import (
    CameraPreviewImageCallback,
    ConnectionStatusCallback,
    DepthcamImageArrivedCallback,
    DeviceStatusCallback,
    IMUDataCallback,
    ImageDataCallback,
    ImageFrame,
    IMUData,
    LidarSinglelayerScanDataInfo,
    LidarScanPoint,
    LidarScanData,
    LidarScanCallback,
    MappingFlagsCallback,
    PoseCovariance,
    PoseAugmentationResultCallback,
    PoseCovarianceCallback,
    PoseSE3,
    SDKListenerStruct,
    SemanticSegmentationImageArrivedCallback,
    TrackingDataCallback,
    TrackingFrame,
)


def _copy_struct(source):
    copied = type(source)()
    ctypes.memmove(ctypes.byref(copied), ctypes.byref(source), ctypes.sizeof(type(source)))
    return copied


class SDKListener:
    """
    Base listener for receiving asynchronous Aurora SDK callbacks.

    Subclass this class and override the callbacks you need. All callbacks are
    invoked on SDK-managed threads, so handlers should return quickly.
    """

    def __init__(self):
        self._callback_refs = {}
        self._user_data = ctypes.pointer(ctypes.py_object(self))
        self._native_listener = SDKListenerStruct()
        self._native_listener.user_data = ctypes.cast(self._user_data, ctypes.c_void_p)
        self._bind_callbacks()

    @property
    def native_listener(self):
        """Return the native listener structure kept alive by this instance."""
        return self._native_listener

    def on_tracking_data(self, tracking_frame):
        """Receive tracking frame updates."""

    def on_raw_image_data(self, timestamp_ns, left_image, right_image):
        """Receive raw stereo image data."""

    def on_pose_augmentation_result(self, timestamp_ns, mode, pose):
        """Receive augmented pose updates."""

    def on_imu_data(self, imu_buffer):
        """Receive IMU samples."""

    def on_mapping_flags(self, flags):
        """Receive mapping flag updates."""

    def on_device_status(self, timestamp_ns, status):
        """Receive device status enum updates."""

    def on_lidar_scan(self, scan_data):
        """Receive single-layer LiDAR scans."""

    def on_camera_preview_image(self, timestamp_ns, left_image, right_image):
        """Receive camera preview frames."""

    def on_connection_status(self, status):
        """Receive connection status updates."""

    def on_depth_camera_data_arrived(self, timestamp_ns):
        """Receive depth camera availability notifications."""

    def on_semantic_segmentation_data_arrived(self, timestamp_ns):
        """Receive semantic segmentation availability notifications."""

    def on_pose_covariance(self, timestamp_ns, covariance):
        """Receive pose covariance updates."""

    def _bind_callbacks(self):
        self._callback_refs["raw_image"] = ImageDataCallback(self._handle_raw_image)
        self._callback_refs["tracking"] = TrackingDataCallback(self._handle_tracking_data)
        self._callback_refs["pose_augmentation"] = PoseAugmentationResultCallback(self._handle_pose_augmentation)
        self._callback_refs["imu"] = IMUDataCallback(self._handle_imu_data)
        self._callback_refs["mapping_flags"] = MappingFlagsCallback(self._handle_mapping_flags)
        self._callback_refs["device_status"] = DeviceStatusCallback(self._handle_device_status)
        self._callback_refs["lidar_scan"] = LidarScanCallback(self._handle_lidar_scan)
        self._callback_refs["camera_preview"] = CameraPreviewImageCallback(self._handle_camera_preview)
        self._callback_refs["connection"] = ConnectionStatusCallback(self._handle_connection_status)
        self._callback_refs["depthcam_arrived"] = DepthcamImageArrivedCallback(self._handle_depthcam_arrived)
        self._callback_refs["semantic_arrived"] = SemanticSegmentationImageArrivedCallback(
            self._handle_semantic_arrived
        )
        self._callback_refs["pose_covariance"] = PoseCovarianceCallback(self._handle_pose_covariance)

        self._native_listener.on_raw_image_data = self._callback_refs["raw_image"]
        self._native_listener.on_tracking_data = self._callback_refs["tracking"]
        self._native_listener.on_pose_augmentation_result = self._callback_refs["pose_augmentation"]
        self._native_listener.on_imu_data = self._callback_refs["imu"]
        self._native_listener.on_mapping_flags = self._callback_refs["mapping_flags"]
        self._native_listener.on_device_status = self._callback_refs["device_status"]
        self._native_listener.on_lidar_scan = self._callback_refs["lidar_scan"]
        self._native_listener.on_camera_preview_image = self._callback_refs["camera_preview"]
        self._native_listener.on_connection_status = self._callback_refs["connection"]
        self._native_listener.on_depthcam_image_arrived = self._callback_refs["depthcam_arrived"]
        self._native_listener.on_semantic_segmentation_image_arrived = self._callback_refs["semantic_arrived"]
        self._native_listener.on_pose_covariance = self._callback_refs["pose_covariance"]

    def _safe_call(self, callback, *args):
        try:
            callback(*args)
        except Exception:
            traceback.print_exc()

    def _copy_image_frame(self, timestamp_ns, desc_ptr, data_ptr):
        if not desc_ptr:
            return None

        desc = _copy_struct(desc_ptr.contents)
        frame_data = None
        if data_ptr and desc.data_size > 0:
            frame_data = ctypes.string_at(data_ptr, desc.data_size)

        frame = ImageFrame.from_c_desc(desc, data=frame_data)
        frame.timestamp_ns = timestamp_ns
        return frame

    def _copy_tracking_frame(self, tracking_info_ptr, buffer_ptr):
        tracking_info = _copy_struct(tracking_info_ptr.contents)
        buffer = buffer_ptr.contents

        left_image_data = None
        right_image_data = None

        if buffer.imgdata_left and tracking_info.left_image_desc.data_size > 0:
            left_image_data = ctypes.string_at(buffer.imgdata_left, tracking_info.left_image_desc.data_size)
        if buffer.imgdata_right and tracking_info.right_image_desc.data_size > 0:
            right_image_data = ctypes.string_at(buffer.imgdata_right, tracking_info.right_image_desc.data_size)

        left_keypoints = []
        for index in range(min(int(tracking_info.keypoints_left_count), int(buffer.keypoints_left_buffer_count))):
            left_keypoints.append(_copy_struct(buffer.keypoints_left[index]))

        right_keypoints = []
        for index in range(min(int(tracking_info.keypoints_right_count), int(buffer.keypoints_right_buffer_count))):
            right_keypoints.append(_copy_struct(buffer.keypoints_right[index]))

        return TrackingFrame.from_c_struct(
            tracking_info,
            left_keypoints=left_keypoints,
            right_keypoints=right_keypoints,
            left_image_data=left_image_data,
            right_image_data=right_image_data,
        )

    def _handle_raw_image(self, _user_data, timestamp_ns, left_desc, left_data, right_desc, right_data):
        left_frame = self._copy_image_frame(timestamp_ns, left_desc, left_data)
        right_frame = self._copy_image_frame(timestamp_ns, right_desc, right_data)
        self._safe_call(self.on_raw_image_data, timestamp_ns, left_frame, right_frame)

    def _handle_tracking_data(self, _user_data, tracking_info, buffer_info):
        tracking_frame = self._copy_tracking_frame(tracking_info, buffer_info)
        self._safe_call(self.on_tracking_data, tracking_frame)

    def _handle_pose_augmentation(self, _user_data, timestamp_ns, mode, pose_ptr):
        pose = _copy_struct(pose_ptr.contents) if pose_ptr else None
        self._safe_call(self.on_pose_augmentation_result, timestamp_ns, mode, pose)

    def _handle_imu_data(self, _user_data, imu_data_ptr, imu_count):
        imu_samples = []
        for index in range(int(imu_count)):
            sample = IMUData()
            ctypes.memmove(ctypes.byref(sample), ctypes.byref(imu_data_ptr[index]), ctypes.sizeof(IMUData))
            imu_samples.append(sample)
        self._safe_call(self.on_imu_data, imu_samples)

    def _handle_mapping_flags(self, _user_data, flags):
        self._safe_call(self.on_mapping_flags, flags)

    def _handle_device_status(self, _user_data, timestamp_ns, status):
        self._safe_call(self.on_device_status, timestamp_ns, status)

    def _handle_lidar_scan(self, _user_data, scan_info_ptr, points_ptr):
        scan_info_ptr = ctypes.cast(scan_info_ptr, ctypes.POINTER(LidarSinglelayerScanDataInfo))
        points_ptr = ctypes.cast(points_ptr, ctypes.POINTER(LidarScanPoint))
        scan_info = _copy_struct(scan_info_ptr.contents)
        scan_points = []
        for index in range(int(scan_info.scan_count)):
            scan_points.append(_copy_struct(points_ptr[index]))
        self._safe_call(self.on_lidar_scan, LidarScanData.from_c_data(scan_info, scan_points))

    def _handle_camera_preview(self, _user_data, timestamp_ns, left_desc, left_data, right_desc, right_data):
        left_frame = self._copy_image_frame(timestamp_ns, left_desc, left_data)
        right_frame = self._copy_image_frame(timestamp_ns, right_desc, right_data)
        self._safe_call(self.on_camera_preview_image, timestamp_ns, left_frame, right_frame)

    def _handle_connection_status(self, _user_data, status):
        self._safe_call(self.on_connection_status, status)

    def _handle_depthcam_arrived(self, _user_data, timestamp_ns):
        self._safe_call(self.on_depth_camera_data_arrived, timestamp_ns)

    def _handle_semantic_arrived(self, _user_data, timestamp_ns):
        self._safe_call(self.on_semantic_segmentation_data_arrived, timestamp_ns)

    def _handle_pose_covariance(self, _user_data, timestamp_ns, covariance_buffer):
        covariance = None
        if covariance_buffer:
            covariance = PoseCovariance()
            ctypes.memmove(
                ctypes.byref(covariance.covariance_matrix),
                covariance_buffer,
                ctypes.sizeof(ctypes.c_float) * 36,
            )
        self._safe_call(self.on_pose_covariance, timestamp_ns, covariance)
