import sys
import cv2
from pypylon import pylon

# Configuration constants
TIMEOUT_MS   = 1000             # Grab timeout in milliseconds
WANTED_PF    = "BayerRG8"      # Desired pixel format
SCALE_FACTOR = 1/3              # Scale down the displayed image by 3x
FPS          = 5               # Desired capture frame rate (fps)


def setup_camera(cam):
    """
    Apply basic configuration to a newly opened camera.
    """
    node_map = cam.GetNodeMap()
    pf_node  = node_map.GetNode("PixelFormat")

    # Attempt to set desired pixel format, fallback on exception
    try:
        pf_node.Value = WANTED_PF
        print(f"[INFO] PixelFormat set to {WANTED_PF}")
    except Exception as e:
        current = getattr(pf_node, "Value", "(unknown)")
        print(f"[WARN] Could not set PixelFormat to {WANTED_PF}: {e}")
        print(f"[INFO] Using fallback format: {current}")

    # Enable and set frame rate
    try:
        cam.AcquisitionFrameRateEnable = True
        # Sensor max throughput ~30MHz / (width×height); clamp to camera limits
        max_fps = 30_000_000 // (cam.Width.Value * cam.Height.Value)
        cam.AcquisitionFrameRate = min(FPS, max_fps)
        print(f"[INFO] AcquisitionFrameRate set to {cam.AcquisitionFrameRate} fps")
    except Exception:
        pass

    # Prepare image converter to BGR8
    converter = pylon.ImageFormatConverter()
    converter.OutputPixelFormat  = pylon.PixelType_BGR8packed
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

    return converter


def get_cameras():
    """
    Discover all GigE Vision Basler cameras on the network.
    Returns a list of tuples: (camera, converter, ip_address).
    """
    tl_factory = pylon.TlFactory.GetInstance()
    devices    = tl_factory.EnumerateDevices()
    cams        = []

    for dev in devices:
        if hasattr(dev, "GetIpAddress"):
            ip  = dev.GetIpAddress()
            cam = pylon.InstantCamera(tl_factory.CreateDevice(dev))
            cam.Open()
            converter = setup_camera(cam)
            cams.append((cam, converter, ip))

    return cams


def main():
    # Discover and open all cameras
    cams = get_cameras()
    if not cams:
        print("[ERROR] No GigE Vision cameras found.")
        sys.exit(1)

    # Print found cameras
    print("[INFO] Found cameras:", [ip for _, _, ip in cams])

    # Start with the first camera
    idx = 0
    cam, converter, ip = cams[idx]
    cam.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    # Prepare display window
    cv2.namedWindow("Basler Live Preview")
    print("[INFO] Use LEFT/RIGHT arrow keys to swap cameras, ESC to quit.")

    # Main grab loop
    while True:
        cam, converter, ip = cams[idx]
        if not cam.IsGrabbing():
            cam.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

        grab = cam.RetrieveResult(TIMEOUT_MS, pylon.TimeoutHandling_ThrowException)
        if grab.GrabSucceeded():
            img = converter.Convert(grab).GetArray()
            # Scale down
            small = cv2.resize(img, (0, 0), fx=SCALE_FACTOR, fy=SCALE_FACTOR)
            cv2.imshow("Basler Live Preview", small)
            key = cv2.waitKey(1)
            grab.Release()

            if key == 27:  # ESC
                break
            elif key == 83:  # RIGHT arrow
                cam.StopGrabbing()
                cam.Close()
                idx = (idx + 1) % len(cams)
                print(f"[INFO] Switched to camera {cams[idx][2]}")
            elif key == 81:  # LEFT arrow
                cam.StopGrabbing()
                cam.Close()
                idx = (idx - 1) % len(cams)
                print(f"[INFO] Switched to camera {cams[idx][2]}")

    # Cleanup
    for cam, _, _ in cams:
        if cam.IsGrabbing():
            cam.StopGrabbing()
        cam.Close()
    cv2.destroyAllWindows()
    print("[INFO] Exiting.")


if __name__ == "__main__":
    main()
