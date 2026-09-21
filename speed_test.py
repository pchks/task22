#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
import time
import urllib.error
import urllib.request


REQUEST_COUNT = 10
CHUNK_SIZE = 1024 * 1024
BYTES_IN_MEGABYTE = 1024 * 1024


def download_once(url: str, timeout: float) -> tuple[int, float]:
    """Скачивает URL целиком и возвращает число байт и затраченное время."""
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "internet-speed-test/1.0",
            "Accept-Encoding": "identity",
            "Cache-Control": "no-cache",
        },
    )

    started_at = time.perf_counter()
    downloaded_bytes = 0

    with urllib.request.urlopen(request, timeout=timeout) as response:
        while chunk := response.read(CHUNK_SIZE):
            downloaded_bytes += len(chunk)

    elapsed = time.perf_counter() - started_at
    return downloaded_bytes, elapsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "10 раз последовательно скачивает файл по URL и измеряет "
            "среднее время запроса и скорость загрузки."
        )
    )
    parser.add_argument("url", help="URL большого файла или изображения")
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="тайм-аут одного запроса в секундах (по умолчанию: 60)",
    )
    args = parser.parse_args()

    if args.timeout <= 0:
        parser.error("--timeout должен быть больше нуля")

    return args


def main() -> int:
    args = parse_args()
    total_bytes = 0
    total_time = 0.0

    print(f"URL: {args.url}")
    print(f"Количество запросов: {REQUEST_COUNT}\n")

    for request_number in range(1, REQUEST_COUNT + 1):
        try:
            downloaded_bytes, elapsed = download_once(args.url, args.timeout)
        except (urllib.error.URLError, OSError, TimeoutError) as error:
            print(
                f"Ошибка в запросе {request_number}/{REQUEST_COUNT}: {error}",
                file=sys.stderr,
            )
            return 1

        total_bytes += downloaded_bytes
        total_time += elapsed

        size_mb = downloaded_bytes / BYTES_IN_MEGABYTE
        speed_mb_s = size_mb / elapsed if elapsed else float("inf")
        print(
            f"[{request_number:2}/{REQUEST_COUNT}] "
            f"{elapsed:8.3f} с | {size_mb:9.2f} МБ | {speed_mb_s:8.2f} МБ/с"
        )

    average_time = total_time / REQUEST_COUNT
    average_size_mb = total_bytes / REQUEST_COUNT / BYTES_IN_MEGABYTE
    total_size_mb = total_bytes / BYTES_IN_MEGABYTE
    average_speed_mb_s = total_size_mb / total_time

    print("\nИтоги:")
    print(f"Среднее время запроса: {average_time:.3f} с")
    print(f"Средний объём ответа:   {average_size_mb:.2f} МБ")
    print(f"Скачано всего:          {total_size_mb:.2f} МБ")
    print(f"Средняя скорость:       {average_speed_mb_s:.2f} МБ/с")
    print(f"                        {average_speed_mb_s * 8:.2f} Мбит/с")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
