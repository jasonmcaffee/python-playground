import asyncio

import nest_asyncio

from projects.slack.services.AIBot import AIBot
from projects.slack.services.SimpleLLM import SimpleLLM

nest_asyncio.apply()


def main():
    print('main')
    simple_llm = SimpleLLM()
    simple_stream_inference_callable = simple_llm.get_simple_stream_inference_callable()
    ai_bot = AIBot(simple_stream_inference_callable)

    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(ai_bot.start_listening_to_slack_events())
        loop.run_forever()
    except KeyboardInterrupt:
        # Handle the interrupt gracefully
        print("Interrupted by user, shutting down.")
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        # Perform any cleanup here if necessary
        loop.stop()
        ai_bot.stop_listening_to_slack_events()

    print('main done')


if __name__ == "__main__":
    main()
