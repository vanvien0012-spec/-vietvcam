ARCHS = arm64
TARGET = iphone:clang:16.5:15.0
INSTALL_TARGET_PROCESSES = VietVCam
THEOS_PACKAGE_SCHEME = rootless

include $(THEOS)/makefiles/common.mk

APPLICATION_NAME = VietVCam

VietVCam_FILES = \
	AppDelegate.m \
	RootViewController.m \
	ControlPanelView.m \
	SourcePanelView.m \
	LightPanelView.m \
	VideoPreviewView.m \
	RTMPPlayerManager.m \
	VCamSettings.m

VietVCam_FRAMEWORKS = UIKit AVFoundation CoreImage CoreMedia QuartzCore
VietVCam_CFLAGS = -fobjc-arc
VietVCam_CODESIGN_FLAGS = -Sentitlements.plist
VietVCam_INFO_PLIST = VietVCam-Info.plist

include $(THEOS_MAKE_PATH)/application.mk

after-package::
	@echo "Built package in packages/"
