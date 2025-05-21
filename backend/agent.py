from pydantic_ai import Agent,RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider
import cv2
model = OpenAIModel(
    'deepseek-chat',
    provider=DeepSeekProvider(api_key='sk-8496415c294241a9b281d91f3dd38480'),
)
agent = Agent(model,deps_type=str,output_type=str)


@agent.tool
async def roulette_wheel(ctx: RunContext[int], square: int) -> str:
    """check if the square is a winner"""
    return 'winner' if square == ctx.deps else 'loser'

@agent.tool
async def image_to_gray(ctx: RunContext[str]) -> str:
    import glob
    image_list = glob.glob(f"{ctx.deps}/*.png")
    for image in image_list:
        try:
            img = cv2.imread(image)
            if img is None:
                return f" Failed to load image: {image} "
            gray = cv2.cvtColor(img,cv2.COLOR_BGRA2GRAY)
            cv2.imwrite(r"F:\deeplearning\image\222\gray.jpg",gray)
            return f"Pic gray is ready"
        except Exception as e:
            return f"Error:{str(e)}"
    return f"All pics is ready"



pic_str = r"F:\deeplearning\image\222"

result = agent.run_sync('help me convert the picture into a grayscale image', deps=pic_str)
print(result)

# # Run the agent
# success_number = 5
# result = agent.run_sync('Put my money on square eighteen', deps=success_number)
# print(result)
# #> True
#
# result = agent.run_sync('I bet five is the winner', deps=success_number)
# print(result)
# #> False