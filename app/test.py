import numpy as np
from model.redis_vector_storage import RedisVectorStorage
from model.clip_embedding_model import CLIPEmbeddingModel
from model.factory import SearchSystemFactory  

search_system_factory = SearchSystemFactory()
search_system = search_system_factory.create()

def create_sample_embeddings(dim=512):
    """Create random sample embeddings for testing"""
    return np.random.rand(dim).astype(np.float32)

def test_redis_vector_storage():
    """Test the Redis vector storage with sample data"""
    
    print("🚀 Starting Redis Vector Storage Test")
    print("=" * 50)
    
    # Initialize the storage
    store = RedisVectorStorage()

    # Sample product data
    sample_products = [
        {
            "sku": "IPHONE-15-128GB",
            "attribute_set_code": "phones",
            "product_type": "simple",
            "categories": "electronics, smartphones, mobile devices",
            "name": "iPhone 15 128GB",
            "description": "Latest iPhone with advanced camera system",
            "price": 799.99
        },
        {
            "sku": "SAMSUNG-S24-256GB",
            "attribute_set_code": "phones",
            "product_type": "simple",
            "categories": "electronics, smartphones, android",
            "name": "Samsung Galaxy S24 256GB",
            "description": "Premium Android smartphone with AI features",
            "price": 899.99
        },
        {
            "sku": "MACBOOK-AIR-M2",
            "attribute_set_code": "computers",
            "product_type": "simple",
            "categories": "electronics, laptops, computers",
            "name": "MacBook Air M2",
            "description": "Ultra-thin laptop with Apple M2 chip",
            "price": 1199.99
        },
        {
            "sku": "DELL-XPS-13",
            "attribute_set_code": "computers",
            "product_type": "simple",
            "categories": "electronics, laptops, windows",
            "name": "Dell XPS 13",
            "description": "Premium Windows ultrabook",
            "price": 1099.99
        },
        {
            "sku": "AIRPODS-PRO",
            "attribute_set_code": "audio",
            "product_type": "simple",
            "categories": "electronics, headphones, wireless",
            "name": "AirPods Pro",
            "description": "Active noise cancellation wireless earbuds",
            "price": 249.99
        },
        {
            "sku": "APPLE-WATCH-9",
            "attribute_set_code": "wearables",
            "product_type": "simple",
            "categories": "electronics, smartwatches, fitness",
            "name": "Apple Watch Series 9",
            "description": "Smartwatch with health tracking and fitness features",
            "price": 399.99
        },
        {
            "sku": "GALAXY-TAB-S9",
            "attribute_set_code": "tablets",
            "product_type": "simple",
            "categories": "electronics, tablets, android",
            "name": "Samsung Galaxy Tab S9",
            "description": "High-end Android tablet with AMOLED display",
            "price": 749.99
        },
        {
            "sku": "IPAD-PRO-M4",
            "attribute_set_code": "tablets",
            "product_type": "simple",
            "categories": "electronics, tablets, apple",
            "name": "iPad Pro M4",
            "description": "Powerful tablet with M4 chip and Liquid Retina XDR display",
            "price": 999.99
        },
        {
            "sku": "SONY-WH1000XM5",
            "attribute_set_code": "audio",
            "product_type": "simple",
            "categories": "electronics, headphones, noise cancelling",
            "name": "Sony WH-1000XM5",
            "description": "Industry-leading noise cancelling over-ear headphones",
            "price": 379.99
        },
        {
            "sku": "LOGITECH-MX-MASTER-3S",
            "attribute_set_code": "accessories",
            "product_type": "simple",
            "categories": "electronics, accessories, mouse",
            "name": "Logitech MX Master 3S",
            "description": "Ergonomic wireless mouse with precision tracking",
            "price": 99.99
        },
        {
            "sku": "NIKON-Z50",
            "attribute_set_code": "cameras",
            "product_type": "simple",
            "categories": "electronics, cameras, photography",
            "name": "Nikon Z50 Mirrorless Camera",
            "description": "Compact mirrorless camera with 4K video support",
            "price": 999.99
        },
        {
            "sku": "PS5-DIGITAL",
            "attribute_set_code": "gaming",
            "product_type": "simple",
            "categories": "electronics, gaming, consoles",
            "name": "PlayStation 5 Digital Edition",
            "description": "Next-gen gaming console with ray tracing and SSD storage",
            "price": 499.99
        },
        {
            "sku": "NINTENDO-SWITCH-OLED",
            "attribute_set_code": "gaming",
            "product_type": "simple",
            "categories": "electronics, gaming, handheld",
            "name": "Nintendo Switch OLED",
            "description": "Handheld gaming console with vibrant OLED display",
            "price": 349.99
        }
    ]

    
    print("📦 Inserting sample products...")
    for product in sample_products:
        search_system.insert_product(product)
        print(f"  ✅ Inserted product {product['name']}")


def test_redis_vector_search():
    """Test the Redis vector search with sample data"""
    print("🚀 Starting Redis Vector Search Test")
    print("=" * 50)

    # Perform a search
    results = search_system.text_search(
        query="elephant in the wild",
        top_k=1
    )

    print(results)

if __name__ == "__main__":
    try:
        # test_redis_vector_storage()
        test_redis_vector_search()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()




