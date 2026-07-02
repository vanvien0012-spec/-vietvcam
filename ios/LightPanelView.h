#import <UIKit/UIKit.h>

@interface LightPanelView : UIView

@property (nonatomic, copy) void (^onSettingsChanged)(void);

- (instancetype)initWithFrame:(CGRect)frame;

@end
