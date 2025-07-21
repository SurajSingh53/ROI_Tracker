import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import random

# Set random seed for reproducible data
np.random.seed(42)
random.seed(42)

# Define realistic data for HealthKart brands and products
brands = ['MuscleBlaze', 'HKVitals', 'Gritzo']
products = {
    'MuscleBlaze': ['Biozyme Performance Whey', 'Mass Gainer XXL', 'Creatine Monohydrate', 'Pre Workout WrathX', 'BCAA Pro'],
    'HKVitals': ['Omega 3 Fatty Acids', 'Multivitamin Women', 'Skin Radiance Collagen', 'Calcium Magnesium Zinc', 'Fish Oil Gold'],
    'Gritzo': ['SuperMilk Daily Nutrition', 'Growth Protein Powder', 'Height Plus Formula', 'Brain Development Supplement', 'Immunity Booster']
}

platforms = ['Instagram', 'YouTube', 'Twitter', 'Facebook']
categories = ['Fitness', 'Nutrition', 'Lifestyle', 'Sports', 'Health']
genders = ['Male', 'Female', 'Other']

# Generate influencers dataset
n_influencers = 150
influencers_data = []

for i in range(n_influencers):
    influencer_id = f"INF_{str(i+1).zfill(3)}"
    category = np.random.choice(categories)
    platform = np.random.choice(platforms)
    
    # Follower count distribution based on platform and category
    if platform == 'YouTube':
        follower_count = int(np.random.lognormal(13, 1.2))  # Higher for YouTube
    elif platform == 'Instagram':
        follower_count = int(np.random.lognormal(12, 1.5))
    else:
        follower_count = int(np.random.lognormal(11, 1.8))
    
    follower_count = min(follower_count, 10000000)  # Cap at 10M
    follower_count = max(follower_count, 1000)  # Min at 1K
    
    influencers_data.append({
        'influencer_id': influencer_id,
        'name': f"Influencer_{i+1}",
        'category': category,
        'gender': np.random.choice(genders),
        'follower_count': follower_count,
        'platform': platform,
        'engagement_rate': round(np.random.normal(3.5, 1.2), 2),
        'avg_views': int(follower_count * np.random.uniform(0.05, 0.3)),
        'location': np.random.choice(['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 'Pune', 'Hyderabad'])
    })

influencers_df = pd.DataFrame(influencers_data)

# Generate posts dataset
n_posts = 800
posts_data = []

start_date = datetime.now() - timedelta(days=180)

for i in range(n_posts):
    influencer = influencers_df.sample(1).iloc[0]
    post_date = start_date + timedelta(days=np.random.randint(0, 180))
    
    # Engagement varies based on platform and follower count
    reach_multiplier = np.random.uniform(0.1, 0.8)
    reach = int(influencer['follower_count'] * reach_multiplier)
    
    engagement_rate = max(0.5, np.random.normal(influencer['engagement_rate'], 0.8))
    likes = int(reach * engagement_rate / 100)
    comments = int(likes * np.random.uniform(0.02, 0.1))
    
    posts_data.append({
        'post_id': f"POST_{str(i+1).zfill(4)}",
        'influencer_id': influencer['influencer_id'],
        'platform': influencer['platform'],
        'date': post_date.strftime('%Y-%m-%d'),
        'url': f"https://{influencer['platform'].lower()}.com/post/{i+1}",
        'caption': f"Check out this amazing product! #HealthKart #{np.random.choice(list(products.keys()))}",
        'reach': reach,
        'likes': likes,
        'comments': comments,
        'shares': int(likes * np.random.uniform(0.01, 0.05)),
        'saves': int(likes * np.random.uniform(0.02, 0.08)) if influencer['platform'] == 'Instagram' else 0
    })

posts_df = pd.DataFrame(posts_data)

# Generate tracking data for campaign attribution
n_tracking_records = 2000
tracking_data = []

sources = ['organic', 'influencer_post', 'story', 'reel', 'youtube_video']
campaigns = ['Summer_Fitness_2024', 'New_Year_Health', 'Monsoon_Immunity', 'Protein_Awareness', 'Women_Wellness']

for i in range(n_tracking_records):
    brand = np.random.choice(brands)
    product = np.random.choice(products[brand])
    campaign = np.random.choice(campaigns)
    source = np.random.choice(sources)
    
    # Generate user activity
    date = start_date + timedelta(days=np.random.randint(0, 180))
    
    # Conversion probability based on source
    conversion_prob = {
        'influencer_post': 0.08,
        'story': 0.12,
        'reel': 0.15,
        'youtube_video': 0.06,
        'organic': 0.03
    }[source]
    
    orders = 1 if np.random.random() < conversion_prob else 0
    
    if orders > 0:
        # Revenue varies by product category
        base_price = {
            'MuscleBlaze': np.random.uniform(1500, 6000),
            'HKVitals': np.random.uniform(500, 2000),
            'Gritzo': np.random.uniform(800, 1500)
        }[brand]
        revenue = round(base_price * np.random.uniform(0.8, 1.3), 2)
    else:
        revenue = 0
    
    tracking_data.append({
        'tracking_id': f"TRK_{str(i+1).zfill(5)}",
        'source': source,
        'campaign': campaign,
        'influencer_id': posts_df.sample(1).iloc[0]['influencer_id'] if source != 'organic' else None,
        'user_id': f"USER_{np.random.randint(1, 50000)}",
        'brand': brand,
        'product': product,
        'date': date.strftime('%Y-%m-%d'),
        'orders': orders,
        'revenue': revenue,
        'clicks': np.random.randint(1, 10) if source != 'organic' else 0,
        'cost_per_click': round(np.random.uniform(0.5, 3.0), 2) if orders > 0 else 0
    })

tracking_df = pd.DataFrame(tracking_data)

# Generate payouts dataset
payouts_data = []
payout_id = 1

for _, influencer in influencers_df.iterrows():
    # Number of campaigns this influencer participated in
    num_campaigns = np.random.randint(1, 5)
    
    for _ in range(num_campaigns):
        basis = np.random.choice(['post', 'order'], p=[0.7, 0.3])
        
        if basis == 'post':
            # Fixed rate per post based on follower count
            if influencer['follower_count'] > 1000000:
                rate = np.random.uniform(50000, 150000)
            elif influencer['follower_count'] > 100000:
                rate = np.random.uniform(10000, 50000)
            elif influencer['follower_count'] > 10000:
                rate = np.random.uniform(2000, 10000)
            else:
                rate = np.random.uniform(500, 2000)
            
            posts_count = np.random.randint(1, 5)
            orders = 0  # Not applicable for per-post payment
            total_payout = rate * posts_count
        else:
            # Commission per order
            rate = np.random.uniform(100, 500)  # Per order commission
            orders = np.random.randint(5, 50)
            total_payout = rate * orders
        
        campaign = np.random.choice(campaigns)
        payout_date = start_date + timedelta(days=np.random.randint(30, 180))
        
        payouts_data.append({
            'payout_id': f"PAY_{str(payout_id).zfill(4)}",
            'influencer_id': influencer['influencer_id'],
            'campaign': campaign,
            'basis': basis,
            'rate': round(rate, 2),
            'posts_count': posts_count if basis == 'post' else 0,
            'orders': orders,
            'total_payout': round(total_payout, 2),
            'payout_date': payout_date.strftime('%Y-%m-%d'),
            'status': np.random.choice(['Paid', 'Pending', 'Processing'], p=[0.7, 0.2, 0.1])
        })
        payout_id += 1

payouts_df = pd.DataFrame(payouts_data)

# Display sample data
print("=== SAMPLE DATASETS ===")
print("\n1. INFLUENCERS DATA:")
print(influencers_df.head())
print(f"Total influencers: {len(influencers_df)}")

print("\n2. POSTS DATA:")
print(posts_df.head())
print(f"Total posts: {len(posts_df)}")

print("\n3. TRACKING DATA:")
print(tracking_df.head())
print(f"Total tracking records: {len(tracking_df)}")

print("\n4. PAYOUTS DATA:")
print(payouts_df.head())
print(f"Total payout records: {len(payouts_df)}")

# Save datasets
influencers_df.to_csv('influencers.csv', index=False)
posts_df.to_csv('posts.csv', index=False)
tracking_df.to_csv('tracking_data.csv', index=False)
payouts_df.to_csv('payouts.csv', index=False)

print("\n=== DATASETS SAVED ===")
print("✓ influencers.csv")
print("✓ posts.csv") 
print("✓ tracking_data.csv")
print("✓ payouts.csv")