#import "ControlPanelView.h"
#import "RTMPPlayerManager.h"
#import "VCamSettings.h"

@implementation ControlPanelView

- (instancetype)initWithFrame:(CGRect)frame player:(RTMPPlayerManager *)player {
    self = [super initWithFrame:frame];
    if (self) {
        _playerManager = player;
        self.backgroundColor = [[UIColor darkGrayColor] colorWithAlphaComponent:0.92];
        self.layer.cornerRadius = 12;
        self.layer.borderWidth = 2;
        self.layer.borderColor = [UIColor colorWithRed:0.82 green:0.70 blue:0.29 alpha:1].CGColor;
        [self buildUI];
    }
    return self;
}

- (UIButton *)btn:(NSString *)title color:(UIColor *)color action:(SEL)action {
    UIButton *b = [UIButton buttonWithType:UIButtonTypeSystem];
    [b setTitle:title forState:UIControlStateNormal];
    b.backgroundColor = color;
    [b setTitleColor:UIColor.whiteColor forState:UIControlStateNormal];
    b.titleLabel.font = [UIFont boldSystemFontOfSize:15];
    b.layer.cornerRadius = 8;
    [b addTarget:self action:action forControlEvents:UIControlEventTouchUpInside];
    return b;
}

- (void)buildUI {
    UIStackView *row1 = [[UIStackView alloc] init];
    row1.axis = UILayoutConstraintAxisHorizontal;
    row1.distribution = UIStackViewDistributionFillEqually;
    row1.spacing = 8;
    [row1 addArrangedSubview:[self btn:@"←" color:[UIColor colorWithRed:0.16 green:0.72 blue:0.85 alpha:1] action:@selector(left)]];
    [row1 addArrangedSubview:[self btn:@"⟲" color:[UIColor grayColor] action:@selector(resetPos)]];
    [row1 addArrangedSubview:[self btn:@"→" color:[UIColor colorWithRed:0.16 green:0.72 blue:0.85 alpha:1] action:@selector(right)]];

    UIStackView *row2 = [[UIStackView alloc] init];
    row2.axis = UILayoutConstraintAxisHorizontal;
    row2.distribution = UIStackViewDistributionFillEqually;
    row2.spacing = 8;
    [row2 addArrangedSubview:[self btn:@"-" color:[UIColor systemRedColor] action:@selector(zoomOut)]];
    [row2 addArrangedSubview:[self btn:@"↓" color:[UIColor systemGreenColor] action:@selector(down)]];
    [row2 addArrangedSubview:[self btn:@"+" color:[UIColor systemRedColor] action:@selector(zoomIn)]];

    UIStackView *row3 = [[UIStackView alloc] init];
    row3.axis = UILayoutConstraintAxisHorizontal;
    row3.distribution = UIStackViewDistributionFillEqually;
    row3.spacing = 8;
    [row3 addArrangedSubview:[self btn:@"Pause" color:[UIColor systemPurpleColor] action:@selector(togglePause)]];
    [row3 addArrangedSubview:[self btn:@"Disable" color:[UIColor systemRedColor] action:@selector(disable)]];

    UIStackView *stack = [[UIStackView alloc] initWithArrangedSubviews:@[row1, row2, row3]];
    stack.axis = UILayoutConstraintAxisVertical;
    stack.spacing = 8;
    stack.translatesAutoresizingMaskIntoConstraints = NO;
    [self addSubview:stack];
    [NSLayoutConstraint activateConstraints:@[
        [stack.topAnchor constraintEqualToAnchor:self.topAnchor constant:10],
        [stack.leadingAnchor constraintEqualToAnchor:self.leadingAnchor constant:10],
        [stack.trailingAnchor constraintEqualToAnchor:self.trailingAnchor constant:-10],
        [stack.bottomAnchor constraintEqualToAnchor:self.bottomAnchor constant:-10],
    ]];
}

- (void)notify {
    [[VCamSettings shared] save];
    if (self.onSettingsChanged) self.onSettingsChanged();
}

- (void)left { [VCamSettings shared].offsetX -= 10; [self notify]; }
- (void)right { [VCamSettings shared].offsetX += 10; [self notify]; }
- (void)down { [VCamSettings shared].offsetY += 10; [self notify]; }
- (void)zoomIn { [VCamSettings shared].zoom = MIN(4, [VCamSettings shared].zoom + 0.1); [self notify]; }
- (void)zoomOut { [VCamSettings shared].zoom = MAX(0.2, [VCamSettings shared].zoom - 0.1); [self notify]; }
- (void)resetPos { [[VCamSettings shared] resetPosition]; [self notify]; }
- (void)togglePause {
    if ([VCamSettings shared].paused) [self.playerManager resume];
    else [self.playerManager pause];
    [self notify];
}
- (void)disable { [self.playerManager disconnect]; [self notify]; }

@end
