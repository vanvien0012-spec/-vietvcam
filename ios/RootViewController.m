#import "RootViewController.h"
#import "VideoPreviewView.h"
#import "RTMPPlayerManager.h"
#import "ControlPanelView.h"
#import "SourcePanelView.h"
#import "LightPanelView.h"
#import "VCamSettings.h"

typedef NS_ENUM(NSInteger, VCamTab) {
    VCamTabControl = 0,
    VCamTabSource = 1,
    VCamTabLight = 2,
};

@implementation RootViewController {
    VideoPreviewView *_preview;
    RTMPPlayerManager *_player;
    UIStackView *_tabBar;
    UIView *_panelContainer;
    ControlPanelView *_controlPanel;
    SourcePanelView *_sourcePanel;
    LightPanelView *_lightPanel;
    VCamTab _activeTab;
}

- (void)viewDidLoad {
    [super viewDidLoad];
    self.view.backgroundColor = [UIColor blackColor];

    _player = [[RTMPPlayerManager alloc] init];
    _preview = [[VideoPreviewView alloc] initWithFrame:CGRectZero];
    _player.previewView = _preview;

    _controlPanel = [[ControlPanelView alloc] initWithFrame:CGRectZero player:_player];
    _sourcePanel = [[SourcePanelView alloc] initWithFrame:CGRectZero player:_player];
    _lightPanel = [[LightPanelView alloc] initWithFrame:CGRectZero];

    __weak typeof(self) weakSelf = self;
    _controlPanel.onSettingsChanged = ^{ [weakSelf refreshPreview]; };
    _lightPanel.onSettingsChanged = ^{ [weakSelf refreshPreview]; };

    _panelContainer = [[UIView alloc] init];
    _tabBar = [self makeTabBar];
    _activeTab = VCamTabControl;

    for (UIView *v in @[_preview, _tabBar, _panelContainer]) {
        v.translatesAutoresizingMaskIntoConstraints = NO;
        [self.view addSubview:v];
    }
    [self showPanelForTab:VCamTabControl];

    [NSLayoutConstraint activateConstraints:@[
        [_preview.topAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.topAnchor constant:8],
        [_preview.leadingAnchor constraintEqualToAnchor:self.view.leadingAnchor constant:8],
        [_preview.trailingAnchor constraintEqualToAnchor:self.view.trailingAnchor constant:-8],
        [_preview.heightAnchor constraintEqualToAnchor:self.view.heightAnchor multiplier:0.42],

        [_tabBar.topAnchor constraintEqualToAnchor:_preview.bottomAnchor constant:10],
        [_tabBar.leadingAnchor constraintEqualToAnchor:self.view.leadingAnchor constant:12],
        [_tabBar.trailingAnchor constraintEqualToAnchor:self.view.trailingAnchor constant:-12],
        [_tabBar.heightAnchor constraintEqualToConstant:34],

        [_panelContainer.topAnchor constraintEqualToAnchor:_tabBar.bottomAnchor constant:8],
        [_panelContainer.leadingAnchor constraintEqualToAnchor:self.view.leadingAnchor constant:12],
        [_panelContainer.trailingAnchor constraintEqualToAnchor:self.view.trailingAnchor constant:-12],
        [_panelContainer.bottomAnchor constraintLessThanOrEqualToAnchor:self.view.safeAreaLayoutGuide.bottomAnchor constant:-12],
        [_panelContainer.heightAnchor constraintGreaterThanOrEqualToConstant:180],
    ]];

    VCamSettings *s = [VCamSettings shared];
    if (s.connected && s.rtmpURL.length > 0) {
        [_player connectURL:s.rtmpURL];
    }
}

- (UIStackView *)makeTabBar {
    NSArray *titles = @[@"Control", @"Source", @"Light"];
    NSMutableArray *buttons = [NSMutableArray array];
    for (NSInteger i = 0; i < titles.count; i++) {
        UIButton *b = [UIButton buttonWithType:UIButtonTypeSystem];
        [b setTitle:titles[i] forState:UIControlStateNormal];
        b.tag = i;
        b.layer.cornerRadius = 8;
        b.titleLabel.font = [UIFont boldSystemFontOfSize:12];
        [b addTarget:self action:@selector(tabTapped:) forControlEvents:UIControlEventTouchUpInside];
        [buttons addObject:b];
    }
    UIStackView *bar = [[UIStackView alloc] initWithArrangedSubviews:buttons];
    bar.axis = UILayoutConstraintAxisHorizontal;
    bar.spacing = 6;
    bar.distribution = UIStackViewDistributionFillEqually;
    [self styleTabBar];
    return bar;
}

- (void)styleTabBar {
    for (UIButton *b in _tabBar.arrangedSubviews) {
        BOOL active = b.tag == _activeTab;
        b.backgroundColor = active ? [UIColor systemBlueColor] : [UIColor lightGrayColor];
        [b setTitleColor:active ? UIColor.whiteColor : UIColor.blackColor forState:UIControlStateNormal];
    }
}

- (void)tabTapped:(UIButton *)sender {
    _activeTab = (VCamTab)sender.tag;
    [self styleTabBar];
    [self showPanelForTab:_activeTab];
}

- (void)showPanelForTab:(VCamTab)tab {
    for (UIView *v in _panelContainer.subviews) [v removeFromSuperview];
    UIView *panel = _controlPanel;
    if (tab == VCamTabSource) panel = _sourcePanel;
    if (tab == VCamTabLight) panel = _lightPanel;
    panel.translatesAutoresizingMaskIntoConstraints = NO;
    [_panelContainer addSubview:panel];
    [NSLayoutConstraint activateConstraints:@[
        [panel.topAnchor constraintEqualToAnchor:_panelContainer.topAnchor],
        [panel.leadingAnchor constraintEqualToAnchor:_panelContainer.leadingAnchor],
        [panel.trailingAnchor constraintEqualToAnchor:_panelContainer.trailingAnchor],
        [panel.bottomAnchor constraintEqualToAnchor:_panelContainer.bottomAnchor],
    ]];
}

- (void)refreshPreview {
    [_preview applySettings];
}

@end
