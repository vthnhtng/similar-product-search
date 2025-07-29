import os
from flask import Flask, request, jsonify, render_template, send_from_directory, url_for
from werkzeug.utils import secure_filename
from model.factory.search_system_factory import SearchSystemFactory

# Initialize search system
search_system_factory = SearchSystemFactory()
search_system = search_system_factory.create()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions for image upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def transform_search_results(results):
    """Transform search results from Redis format to template format"""
    transformed_results = []
    
    for result in results:
        # Convert vector_distance to similarity (1 - distance for cosine similarity)
        similarity = 1 - result.get('vector_distance', 0)
        
        # Create image URL from image_path
        image_url = None
        if result.get('image_path'):
            # If it's a dataset path, serve it from the dataset route
            if result['image_path'].startswith('dataset/'):
                # Extract the relative path from dataset/animal_images/animal/filename
                # Remove 'dataset/' prefix and 'animal_images/' from the path
                relative_path = result['image_path'].replace('dataset/', '').replace('animal_images/', '')
                image_url = f"/dataset/{relative_path}"
            else:
                image_url = result['image_path']
        
        transformed_result = {
            'title': result.get('animal', 'Unknown Animal'),
            'description': result.get('caption', 'No description available'),
            'image_url': image_url,
            'similarity': similarity,
            'content': result.get('caption', 'No content available')  # Fallback for template
        }
        transformed_results.append(transformed_result)
    
    return transformed_results

@app.route('/')
def index():
    """Main page with search interface"""
    return render_template('index.html')

@app.route('/search/text', methods=['POST'])
def text_search():
    """Handle text search requests"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 10)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Perform text search
        textual_results = search_system.text_search(query, top_k)

        # Transform results to match template expectations
        transformed_results = transform_search_results(textual_results)

        return jsonify({
            'success': True,
            'results': transformed_results,
            'query': query
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search/image', methods=['POST'])
def image_search():
    """Handle image search requests"""
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Secure the filename and save the file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Get top_k parameter
            top_k = request.form.get('top_k', 10, type=int)
            
            # Perform image search
            visual_results = search_system.image_search(filepath, top_k)

            # Transform results to match template expectations
            transformed_results = transform_search_results(visual_results)
            
            return jsonify({
                'success': True,
                'results': transformed_results,
                'filename': filename
            })
        else:
            return jsonify({'error': 'Invalid file type. Please upload an image.'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/dataset/<path:filename>')
def dataset_file(filename):
    """Serve dataset files"""
    dataset_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'animal_images')
    full_path = os.path.join(dataset_dir, filename)
    return send_from_directory(dataset_dir, filename)

@app.route('/test')
def test_search():
    """Test endpoint to check if search system is working"""
    try:
        # Test text search with a simple query
        test_results = search_system.text_search("tiger", 5)
        
        return jsonify({
            'success': True,
            'message': 'Search system is working',
            'test_results': test_results,
            'results_count': len(test_results) if test_results else 0
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)