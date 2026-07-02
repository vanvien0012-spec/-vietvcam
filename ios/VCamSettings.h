#import <Foundation/Foundation.h>

@interface VCamSettings : NSObject

@property (nonatomic, copy) NSString *rtmpURL;
@property (nonatomic, assign) BOOL connected;
@property (nonatomic, assign) BOOL paused;
@property (nonatomic, assign) CGFloat offsetX;
@property (nonatomic, assign) CGFloat offsetY;
@property (nonatomic, assign) CGFloat zoom;
@property (nonatomic, assign) CGFloat brightness;
@property (nonatomic, assign) CGFloat contrast;
@property (nonatomic, assign) CGFloat sharpness;
@property (nonatomic, assign) CGFloat lightIntensity;

+ (instancetype)shared;

- (void)save;
- (void)load;
- (void)resetLight;
- (void)resetPosition;

@end
