[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![Downloads][download-shield]][Downloads]
[![License][license-shield]][license]
[![HACS Custom][hacsbadge]][hacs]

# SILAM Pollen Allergy Sensor for Home Assistant

Integration for Home Assistant using the dataset "Best time series obtained from the latest available run." from the SILAM Thredds server to create a service with pollen level sensors for a specific location. The forecast calculation is performed by the Finnish Meteorological Institute, taking into account aerobiological, phenological, and meteorological observation data.

Data source: [https://silam.fmi.fi/pollen.html](https://silam.fmi.fi/pollen.html)

> [!CAUTION]  
> The provided data are unverified model forecasts created for scientific use only.  
> Neither the quality nor the completeness of the information provided is guaranteed, and the data producers bear no responsibility for its accuracy and timeliness.

> [!IMPORTANT]  
> This integration was created using ChatGPT for collaborative coding, bug fixing, and editing.  
> If you adhere to a different ethical viewpoint, I apologize. However, I believe that this application is morally acceptable as the integration is non-commercial, free, and open, and its purpose is to promote openness and interaction.
## 🆕 What's new in v0.2.1

**🌸 Pollen Forecast (BETA)**   
 - Hourly and twice-daily pollen forecasts have added values for selected allergens.  
 - For each pollen sensor, an attribute with the forecast for the next day has been added, which displays the daily forecast for the next day, just like for the pollen index.

[![More details in release v0.2.1](https://img.shields.io/badge/More--in--release-v0.2.1-blue?style=for-the-badge)](https://github.com/danishru/silam_pollen/releases/tag/v0.2.1)

## 🆕 What's new in v0.2.0

- **🌍 Support for two versions of SILAM**  
  Ability to choose between `SILAM Europe (v6.0)` and `SILAM Regional (v5.9.1)` — with automatic availability testing.  
  `SILAM Regional (v5.9.1)` provides more **detailed and accurate forecasts** for Northern and Northwestern Europe.

- **🌸 Pollen Forecast (BETA)**  
  New weather sensor with hourly and twice-daily pollen forecast via `weather.get_forecasts`.

- **📊 Unified Data Handler + Update Service**  
  All data is cached via `data_processing.py`.  
  Added service `SILAM Pollen monitor: Manual update` — can be called manually or in automations.

- **🎨 Icons for integration and sensor**  
  Indicators have become clearer: each allergen now has its own icon.

- **🌐 Localization (in 9 languages)**  
  The interface has been translated into: Danish, English, Finnish, German, Italian, Norwegian, Polish, Russian, Swedish.

[![More details in release v0.2.0](https://img.shields.io/badge/More--in--release-v0.2.0-blue?style=for-the-badge)](https://github.com/danishru/silam_pollen/releases/tag/v0.2.0)

## Description

The **SILAM Pollen** integration provides a service consisting of sensors that dynamically form a URL to request pollen data. Data is requested from the SILAM server via HTTP request, then parsed and updated in Home Assistant. Multiple services can be created for different locations, and there is also the option to select the required types of pollen.

> [!NOTE]
> Please note: the coverage area is limited and depends on the selected dataset.  
> 🟩 **Green** — coverage area of **SILAM Regional (v5.9.1)** (more detailed).  
> 🟨 **Yellow** — coverage area of **SILAM Europe (v6.0)** (more general).  
>  
> To assess coverage and choose the appropriate region, use the interactive map below.

[![Interactive coverage map with pollen level data](https://danishru.github.io/silam_pollen/pollen_area.webp)](https://danishru.github.io/silam_pollen/)

## Installation

### Manual Installation

1. Copy the `silam_pollen` folder to the `custom_components` directory of your Home Assistant configuration.
2. Restart Home Assistant.
3. Add the integration via the web interface:
   - Go to **Settings → Integrations**.
   - Click **Add Integration** and select **SILAM Pollen**.
   - Fill in the required fields (e.g., name, coordinates, altitude, pollen type selection, polling interval).

### Installation via HACS

**Make sure HACS is installed:**  
If HACS is not yet installed, follow the [official HACS installation instructions](https://hacs.xyz/docs/use/).

#### One-click Installation

To install the **SILAM Pollen** integration, click the link below:  

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=danishru&repository=silam_pollen&category=integration)

#### Regular Installation via HACS

1. **Open Home Assistant and go to HACS:**  
   On the sidebar, find and click the HACS icon.
2. **Adding a Custom Repository:**  
   - In HACS, go to the **Integrations** tab.
   - Click the **Add Custom Repository** button.
   - In the pop-up window, enter the repository URL:  
     `https://github.com/danishru/silam_pollen`  
   - Select the repository type **Integration**.
   - Click **Add**.
3. **Installing the Integration:**  
   - After adding the repository, HACS will automatically detect the release of your integration.
   - In the **Integrations** section, the integration named **SILAM Pollen** will appear.
   - Find it and click **Install**.
   - Wait for the installation to complete.

Now your integration is installed and ready to use via HACS!

## Configuration

Go to the link below and follow the setup wizard instructions for **SILAM Pollen**:  

[![Open your Home Assistant instance and show an integration.](https://my.home-assistant.io/badges/integration.svg)](https://my.home-assistant.io/redirect/integration/?domain=silam_pollen)

Or open **Settings → Integrations** in Home Assistant, find `SILAM Pollen`, and follow the setup wizard instructions.

Here you can set parameters for the correct operation of the integration:

- **Observation Zone** – allows you to select a configured zone in your Home Assistant. By default, the zone "Home" is selected.
- **Pollen Type** – selection of the observed pollen. You can choose none or select several from the list.
- **Update Interval** – interval for loading data from the SILAM Thredds server in minutes (default 60, minimum value — 30 minutes).
- **Pollen Forecast (BETA)** – includes an additional weather sensor with pollen level forecast. May increase API response time.
- **Zone Name** – by default, the name from the selected zone is used. This name is used to form the names of services and sensors. The parameter can be overridden.
- **Altitude** – altitude above sea level used for retrieving pollen level data from the dataset. If the zone "Home" is selected, data is taken from general settings (`config/general`); otherwise, the default value is set to 275. The parameter can be overridden.
- **Location** – displays the location of the selected zone on the map. The observation zone can be changed using the map or manually entering the coordinates "Latitude" and "Longitude". The specified radius reflects the approximate spatial resolution of the pollen data (about 10 km).

## Usage

After installing the integration, a service named `SILAM Pollen - {Zone Name}` is created in Home Assistant. The service description includes the coordinates of the observation location and the version of the dataset used.

![image](https://github.com/user-attachments/assets/5d060b47-e758-4d4c-9325-0188d991bfee)

Within the service, a **Pollen Index** sensor is created, the state of which displays the localized value corresponding to the numerical index calculated based on hourly averages and threshold values from the reference table by Mikhail Sofiev ([link](https://www.researchgate.net/profile/Mikhail-Sofiev)). 

Possible index values:
- 1 – Very low
- 2 – Low
- 3 – Moderate
- 4 – High
- 5 – Very high
- If the value does not correspond to any of the specified levels, "Unknown" is displayed.

Additionally, the forecast date and the main allergen significantly affecting the index formation are recorded in the sensor attributes.

If a pollen type is selected, a separate sensor is created for each selected type, displaying a rounded whole number representing the modeled amount of pollen (units per cubic meter). In the attributes of such sensors, the nearest available altitude above sea level used for retrieving data is also indicated.

|  ![image](https://github.com/user-attachments/assets/99a5e8a3-303c-4c7c-b885-a70c5e54269b) | ![image](https://github.com/user-attachments/assets/dbc735f0-10f0-4a88-8fbb-1dbc5d98f5eb)  |
| ------------- | ------------- |

If the **Pollen Forecast (BETA)** option is enabled, an additional **weather sensor** will be created, which provides:
- hourly forecast for 24 hours (with a 3-hour step),
- and a twice-daily forecast for 36 hours ahead.

The state of the weather sensor displays the **pollen index for the first available time interval of the hourly forecast**.  

![image](https://github.com/user-attachments/assets/fe9bc3ce-8d86-444a-b768-243fe3ec66fa)

This data is available through the standard service `weather.get_forecasts`.

![image](https://github.com/user-attachments/assets/54f85a99-6b78-4035-a206-5f4aa64e562e)

<details>
<summary>Show example response "Hourly"</summary>

```yaml
weather.silam_pollen_frantsiia_forecast:
  forecast:
    - datetime: "2025-04-10T14:00:00+00:00"
      condition: high
      native_temperature_unit: °C
      pollen_index: 4
      temperature: 15.2
      pollen_alder: 0
      pollen_birch: 260
    - datetime: "2025-04-10T17:00:00+00:00"
      condition: high
      native_temperature_unit: °C
      pollen_index: 4
      temperature: 15.3
      pollen_alder: 0
      pollen_birch: 308
    - datetime: "2025-04-10T20:00:00+00:00"
      condition: high
      native_temperature_unit: °C
      pollen_index: 4
      temperature: 13.7
      pollen_alder: 0
      pollen_birch: 340
    - datetime: "2025-04-10T23:00:00+00:00"
      condition: high
      native_temperature_unit: °C
      pollen_index: 4
      temperature: 10.5
      pollen_alder: 0
      pollen_birch: 264
    - datetime: "2025-04-11T02:00:00+00:00"
      condition: moderate
      native_temperature_unit: °C
      pollen_index: 3
      temperature: 7.8
      pollen_alder: 0
      pollen_birch: 79
    - datetime: "2025-04-11T05:00:00+00:00"
      condition: moderate
      native_temperature_unit: °C
      pollen_index: 3
      temperature: 5.9
      pollen_alder: 0
      pollen_birch: 162
    - datetime: "2025-04-11T08:00:00+00:00"
      condition: high
      native_temperature_unit: °C
      pollen_index: 4
      temperature: 10.3
      pollen_alder: 0
      pollen_birch: 352
    - datetime: "2025-04-11T11:00:00+00:00"
      condition: high
      native_temperature_unit: °C
      pollen_index: 4
      temperature: 16.8
      pollen_alder: 0
      pollen_birch: 332
```
</details>

<details>
<summary>Show example response "Twice Daily"</summary>

```yaml
weather.silam_pollen_frantsiia_forecast:
  forecast:
    - datetime: "2025-04-10T21:00:00+00:00"
      is_daytime: false
      condition: high
      pollen_index: 4
      temperature: 15.3
      pollen_alder: 0
      pollen_birch: 296
      templow: 8.6
    - datetime: "2025-04-11T09:00:00+00:00"
      is_daytime: true
      condition: moderate
      pollen_index: 3
      temperature: 16.8
      pollen_alder: 0
      pollen_birch: 278
      templow: 5.2
    - datetime: "2025-04-11T21:00:00+00:00"
      is_daytime: false
      condition: high
      pollen_index: 4
      temperature: 19.7
      pollen_alder: 0
      pollen_birch: 416
      templow: 12.1
```
</details>

### How the forecast is calculated

The pollen forecast in the **SILAM Pollen** integration is formed based on the SILAM model and aggregated into two types of forecasts:

#### Hourly Forecast (24 hours)
- Built with a 3-hour step.
- For each 3-hour window, the following are calculated:
  - Maximum temperature.
  - Pollen index — median value rounded up to the nearest whole number.
  - Median value for each selected allergen.
- Uses the current date + 24 hours ahead.

#### Twice Daily Forecast (36 hours)
- Data is grouped into 3 intervals of 12 hours (morning/night).
- Calculated:
  - Maximum and minimum temperature.
  - Pollen index — median value over the interval, also rounded up.
  - Median value for each selected allergen.
- Forecasts are fixed at 00:00 and 12:00 (local user time).

#### Used Parameters
- `POLI` — pollen index value.
- `temp_2m` — temperature at a height of 2 meters.

#### Aggregation Technique
- Data from SILAM is parsed from XML and merged by date (`date`).
- Calculations are performed using `statistics.median`, `max`, `min`.
- All forecasts are cached in `merged_data` and available through `weather.get_forecasts`.
 
## Additional Resources

For more detailed information about pollen and its distribution areas, we recommend checking out the following projects:

- **SILAM Pollen (FMI)**  
  [https://silam.fmi.fi/pollen.html](https://silam.fmi.fi/pollen.html)  
  Official source of pollen forecasts from the Finnish Meteorological Institute. Provides 5-day forecasts of pollen distribution across Europe and Northern Europe (birch, grass, olive, ragweed) in collaboration with the European Allergens Network (EAN).

- **Pollen Club**  
  [https://pollen.club/](https://pollen.club/)  
  A joint project of SILAM and Pollen Club, offering forecasts of pollen occurrence for the European part of Russia. The map displays the hourly SILAM forecast and daily forecast for Moscow, with the option to choose the one with higher concentrations.

- **Allergotop: Allergofon**  
  [https://allergotop.com/allergofon](https://allergotop.com/allergofon)  
  A project providing laboratory-research data on pollen monitoring obtained using pollen traps. This data helps determine the sensitivity threshold to allergens and optimize daily activities for allergy sufferers.

- **MyAllergo**  
  [https://myallergo.ru/pylca/](https://myallergo.ru/pylca/)  
  A project publishing daily data from pollen traps in St. Petersburg. Provides information on pollen concentration with convenient color coding, which is especially useful for allergy sufferers.

- **Allergo.Space: Pollen Monitoring**  
  [https://allergo.space/pollen-monitoring/](https://allergo.space/pollen-monitoring/)  
  An informational resource publishing model pollen forecasts collected from open sources (including SILAM data). The project aims to improve the quality of life for allergy sufferers through accurate monitoring of allergens.

- **Yandex Weather – Allergies**  
  [https://yandex.ru/pogoda/allergies](https://yandex.ru/pogoda/allergies)  
  A section of Yandex Weather where the activity of pollen is calculated using a unique formula considering flowering periods, weather conditions, and user feedback to assess the impact of allergens on well-being.

## License

[MIT License](LICENSE)

## Support

If you have any questions or issues, please create an issue in the [repository](https://github.com/danishru/silam_pollen/issues).

<!-- Definitions for badge links -->
[releases-shield]: https://img.shields.io/github/release/danishru/silam_pollen.svg?style=for-the-badge
[releases]: https://github.com/danishru/silam_pollen/releases
[commits-shield]: https://img.shields.io/github/commit-activity/m/danishru/silam_pollen.svg?style=for-the-badge
[commits]: https://github.com/danishru/silam_pollen/commits
[download-shield]: https://img.shields.io/github/downloads/danishru/silam_pollen/total.svg?style=for-the-badge
[downloads]: https://github.com/danishru/silam_pollen/releases
[license-shield]: https://img.shields.io/github/license/danishru/silam_pollen.svg?style=for-the-badge
[license]: https://github.com/danishru/silam_pollen/blob/master/LICENSE
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[hacs]: https://hacs.xyz/
