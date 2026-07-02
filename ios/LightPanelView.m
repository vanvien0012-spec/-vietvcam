#import "LightPanelView.h"
#import "VCamSettings.h"

@implementation LightPanelView {
    UISlider *_brightness;
    UISlider *_contrast;
    UISlider *_sharpness;
    UISlider *_intensity;
}

- (instancetype)initWithFrame:(CGRect)frame {
    self = [super initWithFrame:frame];
    if (self) {
        self.backgroundColor = [[UIColor darkGrayColor] colorWithAlphaComponent:0.92];
        self.layer.cornerRadius = 12;
        self.layer.borderWidth = 2;
        self.layer.borderColor = [UIColor colorWithRed:0.82 green:0.70 blue:0.29 alpha:1].CGColor;
        [self buildUI];
    }
    return self;
}

- (UISlider *)sliderWithTag:(NSInteger)tag min:(float)min max:(float)max value:(float)value {
    UISlider *s = [[UISlider alloc] init];
    s.minimumValue = min;
    s.maximumValue = max;
    s.value = value;
    s.tag = tag;
    [s addTarget:self action:@selector(sliderChanged:) forControlEvents:UIControlEventValueChanged];
    return s;
}

- (UILabel *)label:(NSString *)text {
    UILabel *l = [[UILabel alloc] init];
    l.text = text;
    l.textColor = UIColor.whiteColor;
    l.font = [UIFont systemFontOfSize:12];
    return l;
}

- (void)buildUI {
    VCamSettings *s = [VCamSettings shared];
    _brightness = [self sliderWithTag:1 min:-100 max:100 value:s.brightness];
    _contrast = [self sliderWithTag:2 min:-100 max:100 value:s.contrast];
    _sharpness = [self sliderWithTag:3 min:0 max:100 value:s.sharpness];
    _intensity = [self sliderWithTag:4 min:0 max:100 value:s.lightIntensity * 100];

    UIStackView *stack = [[UIStackView alloc] initWithArrangedSubviews:@[
        [self label:@"Brightness"], _brightness,
        [self label:@"Contrast"], _contrast,
        [self label:@"Sharpness"], _sharpness,
        [self label:@"Light Intensity"], _intensity,
    ]];
    stack.axis = UILayoutConstraintAxisVertical;
    stack.spacing = 6;
    stack.translatesAutoresizingMaskIntoConstraints = NO;
    [self addSubview:stack];

    UIButton *reset = [UIButton buttonWithType:UIButtonTypeSystem];
    [reset setTitle:@"Reset Defaults" forState:UIControlStateNormal];
    reset.backgroundColor = [UIColor grayColor];
    [reset setTitleColor:UIColor.whiteColor forState:UIControlStateNormal];
    reset.layer.cornerRadius = 8;
    [reset addTarget:self action:@selector(resetTapped) forControlEvents:UIControlEventTouchUpInside];
    reset.translatesAutoresizingMaskIntoConstraints = NO;
    [self addSubview:reset];

    [NSLayoutConstraint activateConstraints:@[
        [stack.topAnchor constraintEqualToAnchor:self.topAnchor constant:10],
        [stack.leadingAnchor constraintEqualToAnchor:self.leadingAnchor constant:10],
        [stack.trailingAnchor constraintEqualToAnchor:self.trailingAnchor constant:-10],
        [reset.topAnchor constraintEqualToAnchor:stack.bottomAnchor constant:8],
        [reset.leadingAnchor constraintEqualToAnchor:self.leadingAnchor constant:10],
        [reset.trailingAnchor constraintEqualToAnchor:self.trailingAnchor constant:-10],
        [reset.heightAnchor constraintEqualToConstant:34],
    ]];
}

- (void)sliderChanged:(UISlider *)sender {
    VCamSettings *s = [VCamSettings shared];
    switch (sender.tag) {
        case 1: s.brightness = sender.value; break;
        case 2: s.contrast = sender.value; break;
        case 3: s.sharpness = sender.value; break;
        case 4: s.lightIntensity = sender.value / 100.0; break;
    }
    [s save];
    if (self.onSettingsChanged) self.onSettingsChanged();
}

- (void)resetTapped {
    [[VCamSettings shared] resetLight];
    _brightness.value = 0;
    _contrast.value = 0;
    _sharpness.value = 0;
    _intensity.value = 50;
    if (self.onSettingsChanged) self.onSettingsChanged();
}

@end
