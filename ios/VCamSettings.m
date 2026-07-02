#import "VCamSettings.h"

static NSString *const kPrefsPath = @"/var/jb/var/mobile/Library/Preferences/com.vanvi.vietvcam.plist";

@implementation VCamSettings

+ (instancetype)shared {
    static VCamSettings *instance;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        instance = [[VCamSettings alloc] init];
        [instance load];
    });
    return instance;
}

- (instancetype)init {
    self = [super init];
    if (self) {
        _rtmpURL = @"rtmp://127.0.0.1:1935/live/cam1";
        _connected = NO;
        _paused = NO;
        _offsetX = 0;
        _offsetY = 0;
        _zoom = 1.0;
        _brightness = 0;
        _contrast = 0;
        _sharpness = 0;
        _lightIntensity = 0.5;
    }
    return self;
}

- (void)save {
    NSDictionary *dict = @{
        @"rtmpURL": self.rtmpURL ?: @"",
        @"connected": @(self.connected),
        @"paused": @(self.paused),
        @"offsetX": @(self.offsetX),
        @"offsetY": @(self.offsetY),
        @"zoom": @(self.zoom),
        @"brightness": @(self.brightness),
        @"contrast": @(self.contrast),
        @"sharpness": @(self.sharpness),
        @"lightIntensity": @(self.lightIntensity),
    };
    [dict writeToFile:kPrefsPath atomically:YES];
}

- (void)load {
    NSDictionary *dict = [NSDictionary dictionaryWithContentsOfFile:kPrefsPath];
    if (!dict) return;
    self.rtmpURL = dict[@"rtmpURL"] ?: self.rtmpURL;
    self.connected = [dict[@"connected"] boolValue];
    self.paused = [dict[@"paused"] boolValue];
    self.offsetX = [dict[@"offsetX"] floatValue];
    self.offsetY = [dict[@"offsetY"] floatValue];
    self.zoom = [dict[@"zoom"] floatValue] ?: 1.0;
    self.brightness = [dict[@"brightness"] floatValue];
    self.contrast = [dict[@"contrast"] floatValue];
    self.sharpness = [dict[@"sharpness"] floatValue];
    self.lightIntensity = [dict[@"lightIntensity"] floatValue] ?: 0.5;
}

- (void)resetLight {
    self.brightness = 0;
    self.contrast = 0;
    self.sharpness = 0;
    self.lightIntensity = 0.5;
    [self save];
}

- (void)resetPosition {
    self.offsetX = 0;
    self.offsetY = 0;
    self.zoom = 1.0;
    [self save];
}

@end
