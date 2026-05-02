"""
train_model.py
--------------
Run this script ONCE locally to train the item category classifier.
It generates category_model.pkl which FastAPI loads at startup.

Usage:
    python train_model.py

Output:
    category_model.pkl
"""

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score

# ---------------------------------------------------------------------------
# Training Data  (item text -> category label)
# Rule: the more examples, the better the accuracy.
# ---------------------------------------------------------------------------
TRAINING_DATA = [
    # --- Electronics ---
    ("lost samsung galaxy phone library",             "Electronics"),
    ("found iphone black color cafeteria",            "Electronics"),
    ("missing android phone cracked screen",          "Electronics"),
    ("lost laptop charger cord brick adapter",        "Electronics"),
    ("found earphones white airpods case",            "Electronics"),
    ("lost bluetooth speaker small portable",         "Electronics"),
    ("missing tablet ipad near classroom",            "Electronics"),
    ("found usb flash drive white color",             "Electronics"),
    ("lost powerbank black small rectangle",          "Electronics"),
    ("found charger cable type c white",              "Electronics"),
    ("lost wireless mouse computer accessories",      "Electronics"),
    ("found headphones over ear black",               "Electronics"),
    ("lost smartwatch apple watch screen",            "Electronics"),
    ("found earbuds tws small case white",            "Electronics"),
    ("missing laptop charger adapter brick",          "Electronics"),
    ("found keyboard wireless small compact",         "Electronics"),
    ("missing camera digital lens cap",               "Electronics"),
    ("lost phone charger plug adapter wall",          "Electronics"),
    ("found memory card microsd adapter",             "Electronics"),
    ("found tablet stylus pen digital",               "Electronics"),
    ("lost gaming controller wireless",               "Electronics"),
    ("found portable hard drive usb",                 "Electronics"),
    ("missing phone case cracked screen protector",   "Electronics"),
    ("lost android tablet screen broken",             "Electronics"),
    ("found bluetooth earphone charging case",        "Electronics"),

    # --- Personal Accessories ---
    ("lost black leather wallet near canteen",        "Personal Accessories"),
    ("found brown wallet with cards inside",          "Personal Accessories"),
    ("missing wristwatch silver metal band",          "Personal Accessories"),
    ("lost umbrella black foldable",                  "Personal Accessories"),
    ("found eyeglasses prescription lenses case",     "Personal Accessories"),
    ("missing sunglasses brown frame",                "Personal Accessories"),
    ("lost wallet bifold dark brown",                 "Personal Accessories"),
    ("found coin purse small yellow",                 "Personal Accessories"),
    ("missing bracelet gold thin",                    "Personal Accessories"),
    ("lost necklace silver chain pendant",            "Personal Accessories"),
    ("found ring gold small size",                    "Personal Accessories"),
    ("lost watch digital black rubber band",          "Personal Accessories"),
    ("found wallet leather slim minimalist",          "Personal Accessories"),
    ("missing reading glasses hard case",             "Personal Accessories"),
    ("lost fan handheld foldable blue",               "Personal Accessories"),
    ("found small mirror compact powder",             "Personal Accessories"),
    ("missing watch analog leather brown strap",      "Personal Accessories"),
    ("lost money clip silver metal cards",            "Personal Accessories"),
    ("found hair clip hair tie accessories",          "Personal Accessories"),
    ("missing wallet card holder thin",               "Personal Accessories"),
    ("lost earrings small gold stud",                 "Personal Accessories"),
    ("found watch broken strap silver",               "Personal Accessories"),
    ("missing umbrella polka dot colored",            "Personal Accessories"),
    ("lost face mask disposable case holder",         "Personal Accessories"),
    ("found eyeglasses blue frame folded",            "Personal Accessories"),

    # --- Bags ---
    ("lost blue jansport backpack classroom",         "Bags"),
    ("found black sling bag strap broken",            "Bags"),
    ("missing gray backpack books inside",            "Bags"),
    ("lost red pouch small zipper",                   "Bags"),
    ("found drawstring bag white gym",                "Bags"),
    ("missing padded bag black shoulder",             "Bags"),
    ("lost tote bag brown canvas",                    "Bags"),
    ("found duffel bag sports blue",                  "Bags"),
    ("missing shoulder bag black leather strap",      "Bags"),
    ("lost lunch bag insulated zipper blue",          "Bags"),
    ("found clear bag transparent zipper",            "Bags"),
    ("missing messenger bag flap brown",              "Bags"),
    ("lost eco bag reusable folded",                  "Bags"),
    ("found backpack pink floral pattern",            "Bags"),
    ("missing waist bag fanny pack black",            "Bags"),
    ("lost paper bag handles white",                  "Bags"),
    ("found mini bag crossbody strap",                "Bags"),
    ("missing trolley luggage small wheels",          "Bags"),
    ("lost gym bag zipper side pocket",               "Bags"),
    ("found string bag net produce",                  "Bags"),
    ("missing backpack black with many pockets",      "Bags"),
    ("lost sling bag padded camera bag",              "Bags"),
    ("found pouch pencil case small zipper",          "Bags"),
    ("missing bag with compartment pockets",          "Bags"),
    ("lost trolley bag school on wheels",             "Bags"),

    # --- Documents ---
    ("lost student id card near gate",                "Documents"),
    ("found school id laminated yellow lanyard",      "Documents"),
    ("missing government id drivers license",         "Documents"),
    ("lost atm card bank slip receipt",               "Documents"),
    ("found paper documents folder envelope",         "Documents"),
    ("missing birth certificate photocopy",           "Documents"),
    ("lost library card student number",              "Documents"),
    ("found printed paper assignment report",         "Documents"),
    ("missing passport booklet dark blue cover",      "Documents"),
    ("lost card membership loyalty card",             "Documents"),
    ("found id card with lanyard",                    "Documents"),
    ("missing class schedule printed paper",          "Documents"),
    ("lost report card grades student",               "Documents"),
    ("found medical certificate hospital paper",      "Documents"),
    ("missing certificate award printed",             "Documents"),
    ("lost registration form university",             "Documents"),
    ("found debit card visa bank",                    "Documents"),
    ("missing voucher discount printed coupon",       "Documents"),
    ("lost clearance form school signed",             "Documents"),
    ("found sss umid id government",                  "Documents"),
    ("missing bus pass card transit",                 "Documents"),
    ("lost student number id printed",                "Documents"),
    ("found paper receipt transaction",               "Documents"),
    ("missing notebook planner schedule",             "Documents"),
    ("lost parking pass sticker card",                "Documents"),

    # --- Keys ---
    ("found car keys keychain parking lot",           "Keys"),
    ("lost house key small silver ring",              "Keys"),
    ("missing motorcycle key fob black",              "Keys"),
    ("found key bunch multiple keys ring",            "Keys"),
    ("lost locker key number tag attached",           "Keys"),
    ("found single key no keychain hallway",          "Keys"),
    ("missing car key remote control fob",            "Keys"),
    ("lost key with unicorn keychain",                "Keys"),
    ("found key ring with three keys",                "Keys"),
    ("missing door key small brass",                  "Keys"),
    ("lost cabinet key tag label",                    "Keys"),
    ("found key house apartment metal",               "Keys"),
    ("missing motorcycle key ignition",               "Keys"),
    ("lost key lanyard attached gym",                 "Keys"),
    ("found small key padlock bike",                  "Keys"),
    ("missing key fob electronic push start",         "Keys"),
    ("lost key duplicate copy spare",                 "Keys"),
    ("found keys dropped near hallway stairs",        "Keys"),
    ("missing key with number tag locker",            "Keys"),
    ("lost car key smart keyless entry",              "Keys"),
    ("found key ring single key no label",            "Keys"),
    ("missing house keys chain multiple",             "Keys"),
    ("lost bike key chain lock",                      "Keys"),
    ("found key left on table canteen",               "Keys"),
    ("missing key dropped outside gate",              "Keys"),

    # --- Clothing ---
    ("lost black hoodie jacket classroom",            "Clothing"),
    ("found blue polo shirt collar",                  "Clothing"),
    ("missing gray sweater left chair",               "Clothing"),
    ("lost white rubber shoes sneakers",              "Clothing"),
    ("found cap hat blue baseball",                   "Clothing"),
    ("missing yellow raincoat folded",                "Clothing"),
    ("lost socks pair white school uniform",          "Clothing"),
    ("found scarf knitted brown winter",              "Clothing"),
    ("missing jacket windbreaker green",              "Clothing"),
    ("lost gloves pair black leather",                "Clothing"),
    ("found school uniform white shirt",              "Clothing"),
    ("missing pants trousers left restroom",          "Clothing"),
    ("lost tie necktie school uniform",               "Clothing"),
    ("found dress skirt maroon uniform",              "Clothing"),
    ("missing blazer formal black",                   "Clothing"),
    ("lost slippers sandals rubber",                  "Clothing"),
    ("found shorts gym class pe",                     "Clothing"),
    ("missing belt black leather buckle",             "Clothing"),
    ("lost swimming trunks gym bag",                  "Clothing"),
    ("found vest sleeveless school uniform",          "Clothing"),
    ("missing rain boots rubber tall",                "Clothing"),
    ("lost jersey sports team numbered",              "Clothing"),
    ("found lab coat white science",                  "Clothing"),
    ("missing apron home economics class",            "Clothing"),
    ("lost winter coat wool thick",                   "Clothing"),

    # --- School Supplies ---
    ("lost scientific calculator casio",              "School Supplies"),
    ("found blue ballpen pen notebook",               "School Supplies"),
    ("missing spiral notebook math notes",            "School Supplies"),
    ("lost ruler pencil case geometry set",           "School Supplies"),
    ("found textbook chemistry hardcover",            "School Supplies"),
    ("missing coloring materials art supplies",       "School Supplies"),
    ("lost eraser white stapler paper clips",         "School Supplies"),
    ("found highlighter marker colored pens",         "School Supplies"),
    ("missing folder clear plastic documents",        "School Supplies"),
    ("lost scissors small craft cutting",             "School Supplies"),
    ("found geometry set compass protractor",         "School Supplies"),
    ("missing pencil case zipper blue",               "School Supplies"),
    ("lost graphing calculator ti",                   "School Supplies"),
    ("found drawing pad sketch book",                 "School Supplies"),
    ("missing correction tape liquid paper",          "School Supplies"),
    ("lost mechanical pencil lead refill",            "School Supplies"),
    ("found set of crayons coloring",                 "School Supplies"),
    ("missing index cards flash cards study",         "School Supplies"),
    ("lost binder clips paper fastener",              "School Supplies"),
    ("found watercolor paint set brush",              "School Supplies"),
    ("missing sticky notes post it",                  "School Supplies"),
    ("lost pen holder cup desk organizer",            "School Supplies"),
    ("found coloring pencils set box",                "School Supplies"),
    ("missing lecture notes printed handout",         "School Supplies"),
    ("lost book library borrowed hardcover",          "School Supplies"),
]

# ---------------------------------------------------------------------------
# Prepare data
# ---------------------------------------------------------------------------
texts  = [item[0] for item in TRAINING_DATA]
labels = [item[1] for item in TRAINING_DATA]

# ---------------------------------------------------------------------------
# Build pipeline: TF-IDF + Logistic Regression
# ---------------------------------------------------------------------------
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=5000,
        sublinear_tf=True,
    )),
    ("clf", LogisticRegression(
        max_iter=1000,
        C=5.0,
        solver="lbfgs",
    )),
])

# ---------------------------------------------------------------------------
# Evaluate with 5-fold cross-validation
# ---------------------------------------------------------------------------
print("Evaluating with 5-fold cross-validation...")
cv_scores = cross_val_score(pipeline, texts, labels, cv=5, scoring="accuracy")
print("  CV Accuracy per fold:", [round(float(s), 2) for s in cv_scores])
print("  Mean Accuracy:        {:.1f}%".format(np.mean(cv_scores) * 100))

# ---------------------------------------------------------------------------
# Train on full dataset and save
# ---------------------------------------------------------------------------
print("\nTraining on full dataset...")
pipeline.fit(texts, labels)

joblib.dump(pipeline, "category_model.pkl")
print("[OK] category_model.pkl saved!")
print("\nStart FastAPI -- it will load the model automatically.")
