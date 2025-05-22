# Book Cover Generation Prompt

Use this prompt to generate high-quality book covers using the image generation script.

## Important: Activate Virtual Environment First

You must activate the virtual environment before running the script to ensure all required dependencies are available:

```bash
# Activate the virtual environment
source /Users/iankonradjohnson/base/abacus/BookDownloader/venv/bin/activate

# Verify activation by checking if openai module is available
python -c "import openai; print('OpenAI module is available')"
```

## Script Usage

After activating the virtual environment, run the script directly:

```bash
# Make sure to run with python3 
python3 /Users/iankonradjohnson/base/abacus/BookDownloader/scripts/generate_image.py \
  --prompt "YOUR_DETAILED_PROMPT_HERE" \
  --output-dir "OUTPUT_DIRECTORY_PATH" \
  --model "gpt-image-1" \
  --size "a4" \
  --filename "cover_name.png" \
  --reference-images "/path/to/image1.jpg" "/path/to/image2.jpg" 
```

## Parameter Details

- `--prompt`: The detailed description of the book cover (see prompt structure below)
- `--output-dir`: Directory where the generated image will be saved
- `--model`: AI model to use (options: "gpt-image-1", "dall-e-3")
- `--size`: Image dimensions (use "a4" or "1024x1792" for book covers)
- `--filename`: Name of the output file (should end with .png)
- `--reference-images`: Optional paths to reference images to guide the generation (GPT-Image-1 only, up to 4 images)

## Prompt Structure

For best results, include these elements in your prompt:

```
Dover architecture book cover for '[TITLE]'. [BACKGROUND_DESCRIPTION] background with [BORDER_DESCRIPTION] decorative border featuring [DECORATIVE_ELEMENTS].

The central illustration shows [DETAILED_ILLUSTRATION_DESCRIPTION] rendered in [ILLUSTRATION_STYLE] with [COLOR_DETAILS].

Title at top in [TYPOGRAPHY_DESCRIPTION] reads '[TITLE]' and subtitle in smaller text reads '[SUBTITLE]'. At bottom: '[ADDITIONAL_TEXT]' in [TEXT_STYLE].

[ADDITIONAL_DESIGN_ELEMENTS].

The overall design [DESIGN_GOAL_DESCRIPTION].
```

## Using Reference Images

Reference images can significantly improve the quality and consistency of generated book covers. Here are some tips:

1. **Reference images work only with the GPT-Image-1 model** (not with DALL-E 3)
2. **Provide up to 4 reference images** that illustrate:
   - Similar book cover layouts or designs you're trying to emulate
   - Specific architectural elements you want to incorporate
   - Style examples of decorative borders, typography, or illustration techniques
   - Color palettes or design aesthetics that match your vision
3. **Combine reference images with detailed prompts** for best results
4. **Use high-quality source images** that clearly show the elements you want to reference

Example with reference images:
```bash
python generate_image.py \
  --prompt "Dover architecture book cover for 'Gothic Cathedrals'..." \
  --model "gpt-image-1" \
  --reference-images "cathedral_cover_example.jpg" "gothic_tracery.jpg" "vintage_book_layout.jpg"
```

## Creative Variations

For diverse designs, consider these approaches:

1. **Color Variations**:
   - Rich dark backgrounds (burgundy, navy, forest green, deep teal)
   - Light backgrounds (cream, pale blue, mint green, soft lavender, champagne)

2. **Illustration Styles**:
   - Detailed line drawings with subtle color washes
   - Cross-section architectural illustrations
   - Exploded view technical drawings
   - Collage of different building elements
   - Period-appropriate artistic interpretations

3. **Creative Concepts**:
   - Stained glass window-inspired design
   - Victorian scrapbook/drafting table collage
   - Architectural panorama or cityscape
   - Blueprint or technical drawing style
   - 3D architectural model representation

## Tips for Best Results

1. Be specific about architectural details and styles
2. Include period-appropriate decorative elements
3. Balance text and illustration elements
4. Use historically accurate color palettes
5. Provide clear direction on the style and mood
6. Include specific details about typography and text placement
7. When using reference images, describe in the prompt how they should influence the design