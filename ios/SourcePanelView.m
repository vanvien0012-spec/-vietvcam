#import "SourcePanelView.h"
#import "RTMPPlayerManager.h"
#import "VCamSettings.h"

@implementation SourcePanelView {
    UITextField *_urlField;
}

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

- (void)buildUI {
    UILabel *title = [[UILabel alloc] init];
    title.text = @"Live Stream (RTMP)";
    title.textColor = UIColor.whiteColor;
    title.font = [UIFont boldSystemFontOfSize:13];

    _urlField = [[UITextField alloc] init];
    _urlField.backgroundColor = [UIColor colorWithRed:0.12 green:0.17 blue:0.27 alpha:1];
    _urlField.textColor = UIColor.whiteColor;
    _urlField.layer.cornerRadius = 8;
    _urlField.placeholder = @"rtmp://ip:1935/live/cam1";
    _urlField.text = [VCamSettings shared].rtmpURL;
    _urlField.autocapitalizationType = UITextAutocapitalizationTypeNone;
    _urlField.autocorrectionType = UITextAutocorrectionTypeNo;
    _urlField.leftView = [[UIView alloc] initWithFrame:CGRectMake(0, 0, 8, 1)];
    _urlField.leftViewMode = UITextFieldViewModeAlways;

    UIButton *connect = [UIButton buttonWithType:UIButtonTypeSystem];
    [connect setTitle:@"Connect" forState:UIControlStateNormal];
    connect.backgroundColor = [UIColor systemBlueColor];
    [connect setTitleColor:UIColor.whiteColor forState:UIControlStateNormal];
    connect.layer.cornerRadius = 8;
    [connect addTarget:self action:@selector(connectTapped) forControlEvents:UIControlEventTouchUpInside];

    UIButton *disconnect = [UIButton buttonWithType:UIButtonTypeSystem];
    [disconnect setTitle:@"Disconnect" forState:UIControlStateNormal];
    disconnect.backgroundColor = [UIColor grayColor];
    [disconnect setTitleColor:UIColor.whiteColor forState:UIControlStateNormal];
    disconnect.layer.cornerRadius = 8;
    [disconnect addTarget:self action:@selector(disconnectTapped) forControlEvents:UIControlEventTouchUpInside];

    UIStackView *buttons = [[UIStackView alloc] initWithArrangedSubviews:@[connect, disconnect]];
    buttons.axis = UILayoutConstraintAxisHorizontal;
    buttons.spacing = 8;
    buttons.distribution = UIStackViewDistributionFillEqually;

    UIStackView *stack = [[UIStackView alloc] initWithArrangedSubviews:@[title, _urlField, buttons]];
    stack.axis = UILayoutConstraintAxisVertical;
    stack.spacing = 8;
    stack.translatesAutoresizingMaskIntoConstraints = NO;
    [self addSubview:stack];
    [NSLayoutConstraint activateConstraints:@[
        [stack.topAnchor constraintEqualToAnchor:self.topAnchor constant:10],
        [stack.leadingAnchor constraintEqualToAnchor:self.leadingAnchor constant:10],
        [stack.trailingAnchor constraintEqualToAnchor:self.trailingAnchor constant:-10],
        [_urlField.heightAnchor constraintEqualToConstant:36],
    ]];
}

- (void)connectTapped {
    NSString *url = _urlField.text ?: @"";
    [self.playerManager connectURL:url];
}

- (void)disconnectTapped {
    [self.playerManager disconnect];
}

@end
