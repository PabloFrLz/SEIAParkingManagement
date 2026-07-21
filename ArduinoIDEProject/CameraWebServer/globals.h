#ifndef GLOBALS_H
#define GLOBALS_H

#include "esp_camera.h"

extern camera_config_t config;
extern bool camera_active;

bool camera_start(); //metodo que inicia a camera
bool camera_stop(); 

#endif