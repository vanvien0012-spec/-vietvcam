#import <UIKit/UIKit.h>
#import <AVFoundation/AVFoundation.h>

@interface VideoPreviewView : UIView

- (void)attachPlayer:(AVPlayer *)player;
- (void)detachPlayer;
- (void)applySettings;

@end
