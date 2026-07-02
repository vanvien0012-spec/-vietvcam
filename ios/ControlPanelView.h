#import <UIKit/UIKit.h>

@class RTMPPlayerManager;

@interface ControlPanelView : UIView

@property (nonatomic, weak) RTMPPlayerManager *playerManager;
@property (nonatomic, copy) void (^onSettingsChanged)(void);

- (instancetype)initWithFrame:(CGRect)frame player:(RTMPPlayerManager *)player;

@end
