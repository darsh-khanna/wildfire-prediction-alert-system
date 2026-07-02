# AI-Based Wildfire Prediction and Alert System

> An edge-AI wildfire prediction and early warning system built using the Renesas RA6E2 microcontroller and environmental sensors that combines embedded systems, machine learning, cloud connectivity, and automated messaging to detect wildfire risks and notify users in real time.

## Overview

Wildfires pose a significant threat to ecosystems, infrastructure, and human life. This project addresses the need for early wildfire detection by integrating environmental sensor data with machine learning models deployed on the **Renesas QC-BEKITPOCZ** development platform. The system continuously monitors environmental conditions, predicts wildfire risk using a hybrid AI model, and automatically issues WhatsApp alerts when hazardous conditions are detected.

Designed as a complete end-to-end solution, the project integrates edge computing, IoT communication, cloud services, database management, and an interactive dashboard into a unified wildfire monitoring platform.

---

## Project Objectives

* Monitor environmental conditions in real time using embedded sensors.
* Predict wildfire risk using machine learning techniques.
* Perform low-power edge inference on the Renesas QC-BEKITPOCZ development platform.
* Provide cloud-based monitoring and data visualization.
* Automatically notify registered users through WhatsApp when wildfire risk exceeds predefined thresholds.

---

## Features

* Real-time monitoring of temperature, humidity, and air quality (AQI)
* Hybrid Random Forest + ULSTM wildfire prediction model
* Low-power edge inference on the Renesas QC-BEKITPOCZ development platform
* Wi-Fi connectivity for cloud synchronization
* Cloud integration using Adafruit IO (MQTT)
* Interactive Streamlit dashboard for visualization and user registration
* Automated WhatsApp notifications using Node.js, Twilio, and MySQL
* Dynamic wildfire risk scaling based on environmental conditions

---

## System Architecture

### Hardware

* Renesas QC-BEKITPOCZ Development Platform

### Software

* Python
* Node.js
* Streamlit
* MySQL

### Machine Learning

* Random Forest Classifier
* ULSTM-based temporal prediction
* Dynamic risk scaling algorithm

### Cloud & Communication

* MQTT Protocol
* Adafruit IO
* Twilio WhatsApp API

---

## Deployment Workflow

1. Environmental sensor data is collected using the Renesas QC-BEKITPOCZ development platform.
2. Sensor readings are processed using the hybrid machine learning model.
3. Wildfire risk is calculated using environmental features and dynamic threshold scaling.
4. Prediction results are published to Adafruit IO using MQTT.
5. The Streamlit dashboard visualizes live sensor readings and wildfire risk predictions.
6. When the predicted wildfire risk exceeds the configured threshold, automated WhatsApp alerts are sent to registered users.

---

## Wildfire Risk Prediction Logic

The prediction model incorporates feature interactions and adaptive thresholding to improve sensitivity under extreme environmental conditions.

```python
# Temperature-Humidity interaction
th_interact = temp * (100 - humidity)

# Temperature-AQI interaction
tp_interact = temp * AQI

# Dynamic threshold scaling
if temp > 35:
    risk *= min(1.5, 1 + 0.05 * (temp - 35))

# Alert threshold
if temp > 50:
    alert_threshold = 0.15
else:
    alert_threshold = 0.40

if risk > alert_threshold:
    send_alert()
```
