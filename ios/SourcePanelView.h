#import <UIKit/UIKit.h>

@class RTMPPlayerManager;

@interface SourcePanelView : UIView

@property (nonatomic, weak) RTMPPlayerManager *playerManager;

- (instancetype)initWithFrame:(CGRect)frame player:(RTMPPlayerManager *)player;

@end
