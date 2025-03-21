from diffusers import DiffusionPipeline

pipe = DiffusionPipeline.from_pretrained("black-forest-labs/FLUX.1-dev")
pipe = pipe.to("mps")

prompt = "Astronaut in a jungle, cold color palette, muted colors, detailed, 512*512"
image = pipe(prompt).images[0]