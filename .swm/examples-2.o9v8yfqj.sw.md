---
title: Examples 2
---
<SwmSnippet path="/objects/objects_api/weather_page_api.py" line="20">

---

&nbsp;

```python
    def _build_weather_url(self, city_id: str) -> str:
        return f"{self.base_url}?id={city_id}&appid={self.api_key}&units=metric"

    async def get_weather_data_by_city_id(self, city_id: str) -> WeatherResponse:
        # Fetch weather data from API
        weather_url = self._build_weather_url(city_id)
        weather_dict = await ApiAccess.execute_get_request_async(weather_url)
```

---

</SwmSnippet>

<SwmMeta version="3.0.0" repo-id="Z2l0aHViJTNBJTNBcGFuZ28tQXV0b21hdGlvbiUzQSUzQWxpb3IyNzc=" repo-name="pango-Automation"><sup>Powered by [Swimm](https://app.swimm.io/)</sup></SwmMeta>
