module ApplicationHelper
  def is_admin?
    false
  end

  def markdown
    @markdown ||= Redcarpet::Markdown.new(Redcarpet::Render::HTML, autolink: true, tables: true)
  end

  def maruku_string(content)
    Maruku.new(content).to_s
  end

  def syntax_highlight(content)
    @formatter ||= Rouge::Formatters::HTMLPygments.new(Rouge::Formatters::HTML.new)
    @lexer ||= Rouge::Lexers::XML.new
    @formatter.format(@lexer.lex(content))
  end

  def truncate_words(text, length=50, trailing=nil)
    if text.nil? || text.length < length
      text
    else
      full_words = ''
      text.split(/\s+/).each do |word|
        if (full_words.length + word.length/2) < length
          full_words << ' ' << word
        end
      end
      if trailing
        full_words << trailing
      end
      full_words
    end
  end

  def truncate_md(content, length=190, trailing='...')
    if content.nil? || content.length < length
      content
    else
      offset = 0
      truncated_content = nil
      while truncated_content.nil?
        if content[length - offset] =~ /\s/
          truncated_content =
              content.slice(0, length - offset) + (trailing.nil? ? '' : trailing)
        elsif length + offset >= content.length
          truncated_content = content
        elsif content[length + offset] =~ /\s/
          truncated_content =
              content.slice(0, length + offset) + (trailing.nil? ? '' : trailing)
        end
        offset += 1
      end
      truncated_content
    end
  end
end
