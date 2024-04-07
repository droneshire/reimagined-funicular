# Open AI API: Improving Efficiency and Reducing Costs

### Optimize Prompt Length

The cleaned_text contains a lot of detailed requirements for the itinerary. While detail is good, ensure that every word is necessary to fulfill the request. Extra tokens increase cost without adding value.

### Adjust Temperature

A temperature of 1 is the most creative setting, leading to more varied outputs. However, for generating an itinerary based on specific criteria, a lower temperature might produce more consistent and focused results, potentially reducing the need for additional tokens to clarify or correct the output.

### Refine Max Tokens

The max_tokens setting determines the maximum length of the generated response. If you find that the responses are consistently shorter than your limit, you can lower max_tokens to save on costs. Analyze the average length of the responses you're getting and adjust accordingly.

### Use top_p Wisely

Setting top_p=1 means the model considers all possible next tokens at each step, which is fine for maximizing creativity but might not be necessary for your use case. Adjusting top_p to a lower value could make the model's responses more focused and concise, potentially reducing token usage.

### Penalties

You've set frequency_penalty and presence_penalty to 0, which is neutral and doesn't influence the model's token choices. Depending on the variety you need in the responses, tweaking these values can help manage repetition and ensure the uniqueness of the places listed, potentially making the responses more efficient.
