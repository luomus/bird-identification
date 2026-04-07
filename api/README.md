# Identifying species using API

Submit data to endpoint `/classify`.

A bare minimum call with mandatory `latitude` and `longitude` parameters looks like this:

```bash
curl -X POST "http://localhost:8000/classify?latitude=60.1699&longitude=24.9384" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@<path_to_audio_file>"
```

Call with all parameters:

```bash
curl -X POST "http://localhost:8000/classify?latitude=60.1699&longitude=24.9384&threshold=0.5&include_sdm=True&include_noise=True&day_of_year=1&chunk_size=500&overlap=1" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@<path_to_audio_file>"
```

#### Note

- Day of year can be set as a parameter, but if not, today's date is used.
