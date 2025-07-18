import pandas as pd
import os
import atexit

def get_records(csv_path, image_path):

    df = pd.read_csv(csv_path, sep=",")  
    # Ensure "Frame" column exists
    if "Frame" in df.columns:
        df["image_path"] = df["Frame"].apply(
            lambda name: f"/images/{name.strip()}" if pd.notna(name) and name.strip() != "" else None
        )
    else:
        print("ERROR: 'Frame' column missing")
        df["image_path"] = None

    records = df.to_dict(orient="records")
    
    return records
        
   

# def html_generator(dir, i):
#     print('html generator running')
#     csv_path = os.path.join(dir, "readings.csv")
#     image_path = os.path.join(dir, "images")

#     records = get_records(csv_path, image_path) 
#     html_path = os.path.join(dir, f"sessiont{i}.html")

#     with open(html_path, "w") as f:
#         f.write("""
#     <!DOCTYPE html>
#     <html lang="en">
#     <head>
#         <meta charset="UTF-8">
#         <title>Session {i} Data</title>
#         <meta name="viewport" content="width=device-width, initial-scale=1">
#         <!-- Bootstrap 5 CDN -->
#         <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
#     </head>
#     <body class="bg-light">
#     <div class="container mt-5">
#         <h1 class="mb-4">Session Data</h1>
#         <div class="table-responsive">
#             <table class="table table-bordered table-hover align-middle text-center">
#                 <thead class="table-dark">
#                     <tr>
#                         <th>Timestamp</th>
#                         <th>Voltage (V)</th>
#                         <th>Angle (deg)</th>
#                         <th>Image</th>
#                     </tr>
#                 </thead>
#                 <tbody>
#     """)

#         for row in records:
#             f.write("                <tr>\n")
#             f.write(f"                    <td>{row['Timestamp']}</td>\n")
#             f.write(f"                    <td>{row['Voltage (V)']}</td>\n")
#             f.write(f"                    <td>{row['Angle (deg)']}</td>\n")
#             image = row.get("Frame", "").strip()
#             if image:
#                 f.write(f"                    <td><img src='images/{image}' class='img-thumbnail' style='max-width: 200px;'></td>\n")
#             else:
#                 f.write("                    <td><em>No image</em></td>\n")
#             f.write("                </tr>\n")

#         f.write("""
#                 </tbody>
#             </table>
#         </div>
#     </div>
#     </body>
#     </html>
#     """)

def html_generator(dir, i):
    import os
    print('html_generator running')

    csv_path = os.path.join(dir, "readings.csv")
    image_path = os.path.join(dir, "images")
    records = get_records(csv_path, image_path)
    html_path = os.path.join(dir, f"sessiont{i}.html")

    with open(html_path, "w") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Session {i} Data</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- Bootstrap + Styling -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
    .image-scroll {{
        height: 80vh;
        overflow-y: auto;
        border: 1px solid #ccc;
        padding: 40px 10px; /* extra vertical padding */
        background-color: white;
        display: flex;
        flex-direction: column;
        align-items: center;
    }}
    .image-scroll img {{
        max-width: 100%;
        margin: 15px 0;
        border-radius: 10px;
    }}
    .image-wrapper {{
        position: relative;
        height: 100%;
        width: 90%;
    }}
    .image-wrapper.highlight::before {{
        content: "";
        position: absolute;
        top: -5px;
        left: -5px;
        right: -5px;
        bottom: -5px;
        border: 3px solid #0d6efd;
        border-radius: 12px;
        box-shadow: 0 0 10px #0d6efd;
        z-index: 1;
    }}
    .image-wrapper:not(.highlight) img {{
        transform: scale(0.5);
        opacity: 1;
    }}
    .image-wrapper.highlight img {{
        transform: scale(1.0);
        opacity: 1;
        z-index: 2;
    }}
</style>

</head>
<body>
<div class="container-fluid mt-4">
    <h1 class="mb-4">Session {i} Data</h1>
    <div class="row">
        <!-- Data Table -->
        <div class="col-md-8">
            <table class="table table-bordered table-hover align-middle text-center" id="data-table">
                <thead class="table-dark">
                    <tr>
                        <th>Timestamp</th>
                        <th>Voltage (V)</th>
                        <th>Angle (deg)</th>
                    </tr>
                </thead>
                <tbody>
""")

        for idx, row in enumerate(records):
            f.write(f"""<tr data-index="{idx}">
    <td>{row['Timestamp']}</td>
    <td>{row['Voltage (V)']}</td>
    <td>{row['Angle (deg)']}</td>
</tr>
""")

        f.write("""            </tbody>
            </table>
        </div>

        <!-- Vertical Image Scroll -->
        <div class="col-md-4">
            <div class="image-scroll" id="image-list">
""")

        for idx, row in enumerate(records):
            image = row.get("Frame", "").strip()
            if image:
                f.write(f"""
<div class="image-wrapper" data-index="{idx}">
    <img src="images/{image}" alt="Image {idx}">
</div>
""")

        f.write("""            </div>
        </div>
    </div>
</div>

<!-- JS -->
<script>
    const rows = document.querySelectorAll("#data-table tbody tr");
    const imageWrappers = document.querySelectorAll(".image-wrapper");
    const imageList = document.getElementById("image-list");

    rows.forEach(row => {
        row.addEventListener("mouseenter", () => {
            const index = row.getAttribute("data-index");

            // Remove highlight from all
            imageWrappers.forEach(div => div.classList.remove("highlight"));

            // Add highlight to current image
            const target = document.querySelector(`.image-wrapper[data-index='${index}']`);
            if (target) {
                target.classList.add("highlight");
                const scrollTop = target.offsetTop - imageList.clientHeight / 2 + target.clientHeight / 2;
                imageList.scrollTop = scrollTop;  // instant jump, no animation
            }
        });
    });
</script>

</body>
</html>""")

        


