#import "VideoPreviewView.h"
#import "VCamSettings.h"
#import <CoreImage/CoreImage.h>

@interface VideoPreviewView ()
@property (nonatomic, strong) AVPlayerLayer *playerLayer;
@property (nonatomic, strong) CALayer *filterLayer;
@property (nonatomic, strong) CIContext *ciContext;
@end

@implementation VideoPreviewView

+ (Class)layerClass {
    return [AVPlayerLayer class];
}

- (instancetype)initWithFrame:(CGRect)frame {
    self = [super initWithFrame:frame];
    if (self) {
        self.backgroundColor = [UIColor blackColor];
        self.playerLayer = (AVPlayerLayer *)self.layer;
        self.playerLayer.videoGravity = AVLayerVideoGravityResizeAspect;
        self.ciContext = [CIContext contextWithOptions:nil];
        self.clipsToBounds = YES;
    }
    return self;
}

- (void)attachPlayer:(AVPlayer *)player {
    self.playerLayer.player = player;
    [self applySettings];
}

- (void)detachPlayer {
    self.playerLayer.player = nil;
}

- (void)applySettings {
    VCamSettings *s = [VCamSettings shared];
    CGFloat scale = MAX(0.2, MIN(4.0, s.zoom));
    CGAffineTransform t = CGAffineTransformIdentity;
    t = CGAffineTransformTranslate(t, s.offsetX, s.offsetY);
    t = CGAffineTransformScale(t, scale, scale);
    self.playerLayer.transform = CATransform3DMakeAffineTransform(t);

    CGFloat brightness = s.brightness / 100.0;
    CGFloat contrast = 1.0 + (s.contrast / 100.0);
    self.playerLayer.opacity = 0.85 + (s.lightIntensity * 0.15);

    if ([self.playerLayer respondsToSelector:@selector(setFilters:)]) {
        CIFilter *color = [CIFilter filterWithName:@"CIColorControls"];
        [color setValue:@(brightness) forKey:kCIInputBrightnessKey];
        [color setValue:@(contrast) forKey:kCIInputContrastKey];
        [color setValue:@(1.0 + s.sharpness / 50.0) forKey:kCIInputSaturationKey];
    }
}

- (void)layoutSubviews {
    [super layoutSubviews];
    [self applySettings];
}

@end
