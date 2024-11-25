import unittest
from msg_split import split_message
from msg_split.exceptions import ParseError, SplitError

class TestSplitMessage(unittest.TestCase):
    
    def test_single_fragment(self):
        """Test when the source message fits within a single chunk with tags."""
        source = '<p>Hello</p><b>World</b>'
        max_len = len(source)
        correct_result = [source]
        
        result = list(split_message(source, max_len))
        
        self.assertEqual(result, correct_result)

    def test_multiple_fragments(self):
        """Test when the source message with tags is longer than max_len."""
        source = '<p>123</p>'
        max_len = 8
        correct_result = ['<p>1</p>', '<p>2</p>', '<p>3</p>']
        
        result = list(split_message(source, max_len))
        
        self.assertEqual(result, correct_result)
        
    def test_hierarchy(self):
        """Test when need to add open and close tags to fragments."""
        source = '<p>123<span><b>Name:</b> <i>John</i></span> Lorem</p>'
        max_len = 32
        correct_result = [  '<p>123<span><b>Na</b></span></p>', 
                            '<p><span><b>me:</b> </span></p>',
                            '<p><span><i>John</i></span> </p>',
                            '<p>Lorem</p>']
        
        result = list(split_message(source, max_len))
        
        self.assertEqual(result, correct_result)
    
    def test_text_before(self):
        """Test when the source message content contains text before first tag."""
        source = 'TEXT<p>123</p>'
        max_len = 8
        correct_result = ['TEXT', '<p>1</p>', '<p>2</p>', '<p>3</p>']
        
        result = list(split_message(source, max_len))
        
        self.assertEqual(result, correct_result)   
    
    def test_text_after(self):
        """Test when the source message content contains text after first tag."""
        source = '<p>123</p>TEXT'
        max_len = 8
        correct_result = ['<p>1</p>', '<p>2</p>', '<p>3</p>', 'TEXT']
        
        result = list(split_message(source, max_len))
        
        self.assertEqual(result, correct_result)
    
        
    def test_only_text(self):
        """Test when the source message content contains only plain text."""
        source = 'Text1Text2'
        max_len = 3
        correct_result = ['Tex', 't1T', 'ext', '2']
        
        result = list(split_message(source, max_len))
        
        self.assertEqual(result, correct_result)

    def test_empty_source(self):
        """Test when the source message is empty."""
        source = ''
        max_len = 8
        correct_result = []
        
        result = list(split_message(source, max_len))
        
        self.assertEqual(result, [])

    # Because validation of source HTML fragment is out of scope - no more tests for it
    def test_unpaired_tag_raises_parse_error(self):
        """Test if unpaired tags raise ParseError."""
        source = '<p>Unpaired tag'
        
        with self.assertRaises(ParseError):
            list(split_message(source))

    def test_unbreakable_chunk_raises_split_error(self):
        """Test if unbreakable non-tag chunks raise SplitError."""
        source = '<article>123</article>'
        max_len = 8
        
        with self.assertRaises(SplitError):
            list(split_message(source, max_len))

    def test_single_large_tag(self):
        """Test handling of a single large tag exceeding max_len."""
        source = f'<strong>123</strong>'
        max_len = 5
        
        with self.assertRaises(SplitError):
            list(split_message(source, max_len))
    
    def test_large_hierarchy(self):
        """Test handling of a hierarchy of tags exceeding max_len."""
        source = f'<p><b> Text <i>123</i></b></p>'
        max_len = 8
        
        with self.assertRaises(SplitError):
            list(split_message(source, max_len))

if __name__ == '__main__':
    unittest.main()
