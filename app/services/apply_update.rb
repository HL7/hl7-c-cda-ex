class ApplyUpdate
  URL = 'https://raw.githubusercontent.com/'
  HTML_URL = 'https://githubusercontent.com/'

  def self.process!(source, update)
    update_parts = update.split('/')
    section = Section.find_or_create_by(name: update_parts[0]) do |t|
      t.section_type = 'sect'
    end

    case update_parts.count
      when 2
        new(source, section, update).update_section
      else
        new(source, section, update).update_example
    end
  end

  def update_section
    if @update_file =~ /readme.md/i
      narrative = RestClient.get URI::encode("#{URL}#{@source}/master/#{@update_file}")
      @section.narrative = narrative
      @section.section_type = narrative =~ /section examples/i ? 'sect' : 'doc'
      @section.save!
      true
    else
      Rails.logger.info("Unknown section file: #{@update_file} ignored")
      false
    end
  end

  def update_example
    update_parts = @update_file.split('/')
    puts 'Retrieving example'
    example = Example.find_or_create_by(name: update_parts[1]) do |t|
      t.section = @section
      t.status = 'draft'
    end

    puts 'Processing update'
    if @update_file =~ /readme.md/i
      response = RestClient.get(URI::encode("#{URL}#{@source}/master/#{@update_file}"))
      metadata = MetadataParser.parse(response).to_h
      approvals = metadata.delete(:approvals)
      example.update!(metadata)
      true
    elsif @update_file =~ /c(-)?cda2.1..xml/i
      example.example_url = URI::encode("#{HTML_URL}#{@source}/blob/master/#{@update_file}")
      example.example = RestClient.get(URI::encode("#{URL}#{@source}/master/#{@update_file}"))
      example.save!
      true
    else
      Rails.logger.info("Unknown section file: #{@update_file} ignored")
      false
    end
  end

  private
  def initialize(source, section, update_file)
    @source = source
    @section = section
    @update_file = update_file
  end
end