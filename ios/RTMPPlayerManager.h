#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>

@class VideoPreviewView;

@interface RTMPPlayerManager : NSObject

@property (nonatomic, weak) VideoPreviewView *previewView;
@property (nonatomic, readonly) BOOL isPlaying;

- (void)connectURL:(NSString *)url;
- (void)disconnect;
- (void)pause;
- (void)resume;

@end
