import datetime
from flask import Flask, request, redirect, jsonify

app = Flask(__name__)

class AppRedirect:
    @staticmethod
    def redirect(options):
        user_agent = request.headers.get('User-Agent')
        browser_moved_to_background = False

        def try_to_open_in_multiple_phases(urls):
            nonlocal browser_moved_to_background
            current_index = 0
            redirect_time = None

            def next_phase():
                nonlocal current_index, redirect_time
                if len(urls) > current_index:
                    if browser_moved_to_background:
                        print('Browser moved to the background, we assume that we are done here')
                        return

                    if redirect_time and (datetime.now() - redirect_time).total_seconds() > 3:
                        print('Enough time has passed, the app is probably open')
                    else:
                        redirect_time = datetime.now()
                        return redirect(urls[current_index])

            return next_phase()

        has_ios = bool(options.get("iosApp") or options.get("iosAppStore"))
        has_android = bool(options.get("android"))
        has_overall_fallback = bool(options.get("overallFallback"))

        if has_ios and ("iPhone" in user_agent or "iPad" in user_agent or "iPod" in user_agent):
            urls = []
            if options.get("iosApp"):
                urls.append(options["iosApp"])
            if options.get("iosAppStore"):
                urls.append(options["iosAppStore"])
            return try_to_open_in_multiple_phases(urls)

        elif has_android and "Android" in user_agent:
            intent = options["android"]
            intent_url = f'intent://{intent["host"]}#Intent;' \
                         f'scheme={intent["scheme"]};' \
                         f'package={intent["package"]};' \
                         f'{f"action={intent['action']};" if intent.get("action") else ""}' \
                         f'{f"category={intent["category"]};" if intent.get("category") else ""}' \
                         f'{f"component={intent["component"]};" if intent.get("component") else ""}' \
                         f'{f"S.browser_fallback_url={intent["fallback"]};" if intent.get("fallback") else ""}' \
                         'end'
            return redirect(intent_url)

        elif has_overall_fallback:
            return redirect(options["overallFallback"])

        else:
            return jsonify({"message": "Unknown platform and no overallFallback URL, nothing to do"}), 400
