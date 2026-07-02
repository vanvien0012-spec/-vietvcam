#import "RTMPPlayerManager.h"
#import "VideoPreviewView.h"
#import "VCamSettings.h"

@interface RTMPPlayerManager ()
@property (nonatomic, strong) AVPlayer *player;
@property (nonatomic, strong) AVPlayerItem *playerItem;
@property (nonatomic, assign) BOOL isPlaying;
@end

@implementation RTMPPlayerManager

- (void)connectURL:(NSString *)url {
    if (url.length == 0) return;
    [self disconnect];

    NSURL *streamURL = [NSURL URLWithString:url];
    if (!streamURL) return;

    self.playerItem = [AVPlayerItem playerItemWithURL:streamURL];
    self.player = [AVPlayer playerWithPlayerItem:self.playerItem];
    [self.previewView attachPlayer:self.player];

    __weak typeof(self) weakSelf = self;
    [self.playerItem addObserver:weakSelf forKeyPath:@"status" options:NSKeyValueObservingOptionNew context:nil];

    [self.player play];
    self.isPlaying = YES;

    VCamSettings *settings = [VCamSettings shared];
    settings.connected = YES;
    settings.rtmpURL = url;
    [settings save];
}

- (void)observeValueForKeyPath:(NSString *)keyPath
                      ofObject:(id)object
                        change:(NSDictionary<NSKeyValueChangeKey,id> *)change
                       context:(void *)context {
    if ([keyPath isEqualToString:@"status"] && object == self.playerItem) {
        if (self.playerItem.status == AVPlayerItemStatusFailed) {
            NSLog(@"[VietVCam] RTMP/HLS play failed: %@", self.playerItem.error);
        }
    }
}

- (void)disconnect {
    if (self.playerItem) {
        @try {
            [self.playerItem removeObserver:self forKeyPath:@"status"];
        } @catch (__unused NSException *e) {}
    }
    [self.player pause];
    self.player = nil;
    self.playerItem = nil;
    self.isPlaying = NO;
    [self.previewView detachPlayer];

    VCamSettings *settings = [VCamSettings shared];
    settings.connected = NO;
    [settings save];
}

- (void)pause {
    [self.player pause];
    self.isPlaying = NO;
    [VCamSettings shared].paused = YES;
    [[VCamSettings shared] save];
}

- (void)resume {
    [self.player play];
    self.isPlaying = YES;
    [VCamSettings shared].paused = NO;
    [[VCamSettings shared] save];
}

@end
