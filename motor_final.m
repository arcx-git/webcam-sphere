/*
 * motor_final.m
 *
 * Logitech Sphere motor control - Unit ID 9 (GUID ...2256)
 *
 * Daemon mode (--daemon):
 *   Reads commands from stdin, runs internal movement loop in C.
 *   Commands:
 *     move <pan> <tilt>   - Start continuous movement (values per tick, 64=1deg)
 *     stop                - Stop movement
 *     step <pan> <tilt>   - Single step
 *     reset               - Center position
 *     quit                - Exit
 *
 * Single command mode:
 *   motor_final <left|right|up|down|reset> [degrees]
 */

#import <Foundation/Foundation.h>
#import "UVCController.h"
#include <pthread.h>

@interface UVCController (MotorControl)
- (BOOL) setData:(void*)value withLength:(int)length forSelector:(int)selector atUnitId:(int)unitId;
- (BOOL) getData:(void*)value ofType:(int)type withLength:(int)length fromSelector:(int)selector atUnitId:(int)unitId;
- (void) setIsInterfaceOpen:(BOOL)isInterfaceOpen;
@end

#define MOTOR_UNIT_ID  9
#define SEL_PANTILT_RELATIVE  1
#define SEL_PANTILT_RESET     2
#define TICK_INTERVAL_US  30000  // 30ms between motor commands

static UVCController *g_ctrl = nil;
static volatile int16_t g_pan = 0;
static volatile int16_t g_tilt = 0;
static volatile BOOL g_running = YES;
static volatile BOOL g_moving = NO;

static void sendPanTilt(int16_t pan, int16_t tilt) {
    uint8_t data[4] = {
        pan & 0xFF, (pan >> 8) & 0xFF,
        tilt & 0xFF, (tilt >> 8) & 0xFF
    };
    [g_ctrl setData:data withLength:4 forSelector:SEL_PANTILT_RELATIVE atUnitId:MOTOR_UNIT_ID];
}

static void sendReset(void) {
    uint8_t data[] = {0x03};
    [g_ctrl setData:data withLength:1 forSelector:SEL_PANTILT_RESET atUnitId:MOTOR_UNIT_ID];
}

static void *motorThread(void *arg) {
    while (g_running) {
        if (g_moving && (g_pan != 0 || g_tilt != 0)) {
            @autoreleasepool {
                sendPanTilt(g_pan, g_tilt);
            }
        }
        usleep(TICK_INTERVAL_US);
    }
    return NULL;
}

static int runDaemon(void) {
    setvbuf(stdin, NULL, _IONBF, 0);

    // Start motor thread
    pthread_t tid;
    pthread_create(&tid, NULL, motorThread, NULL);

    char line[256];
    while (fgets(line, sizeof(line), stdin)) {
        if (strncmp(line, "quit", 4) == 0) break;

        if (strncmp(line, "reset", 5) == 0) {
            g_moving = NO;
            g_pan = 0;
            g_tilt = 0;
            sendReset();
        }
        else if (strncmp(line, "stop", 4) == 0) {
            g_moving = NO;
            g_pan = 0;
            g_tilt = 0;
        }
        else if (strncmp(line, "move ", 5) == 0) {
            int p = 0, t = 0;
            sscanf(line + 5, "%d %d", &p, &t);
            g_pan = (int16_t)p;
            g_tilt = (int16_t)t;
            g_moving = YES;
        }
    }

    g_running = NO;
    g_moving = NO;
    pthread_join(tid, NULL);
    return 0;
}

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        g_ctrl = [UVCController uvcControllerWithVendorId:0x046D productId:0x0994];
        if (!g_ctrl) { fprintf(stderr, "Sphere not found!\n"); return 1; }
        [g_ctrl setIsInterfaceOpen:YES];

        if (argc >= 2 && strcmp(argv[1], "--daemon") == 0) {
            return runDaemon();
        }

        if (argc < 2) {
            printf("Usage: %s <left|right|up|down|reset> [degrees]\n", argv[0]);
            printf("       %s --daemon\n", argv[0]);
            return 0;
        }

        int degrees = (argc >= 3) ? atoi(argv[2]) : 5;
        if (degrees <= 0) degrees = 5;
        int16_t panVal = 0, tiltVal = 0;

        if (strcmp(argv[1], "right") == 0)      panVal = degrees * 64;
        else if (strcmp(argv[1], "left") == 0)   panVal = -(degrees * 64);
        else if (strcmp(argv[1], "up") == 0)     tiltVal = -(degrees * 64);
        else if (strcmp(argv[1], "down") == 0)   tiltVal = degrees * 64;
        else if (strcmp(argv[1], "reset") == 0)  { sendReset(); return 0; }
        else { fprintf(stderr, "Unknown: %s\n", argv[1]); return 1; }

        sendPanTilt(panVal, tiltVal);
    }
    return 0;
}
