class MetadataParser
  STATUS_TRANSLATE = {Approved: 'app', Pending: 'pend', Withdrawn: 'wthd'}
  def self.parse(metadata)
    example_meta = ExampleMetadata.new('pend',false)

    metadata.split(/##+/).each do |group|
      if group.length > 0
        case group
          when /^approval/i
            example_meta[:status], example_meta[:approvals] = parse_approvals(group)
          when /^comments/i
            example_meta[:comments] = parse_comments(group)
          when /^custodian/i
            example_meta[:custodian] = parse_custodian(group)
          when /^reference.*full.*sample/i
            example_meta[:full_sample] = parse_full_sample(group)
          when /^keywords/i
            example_meta[:keywords] = parse_keywords(group)
          when /^validation location/i
            example_meta[:validation] = parse_validation(group)
          when /^c-cda 2.1 example/i
            example_meta[:oids] = parse_oids(group)
          when /^certification/i
            example_meta[:onc_certification] = parse_certifications(group)
          else
            puts '-------- unknown group'
            puts group
        end
      end
    end

    example_meta
  end

  private
  def self.parse_comments(chunk)
    content = chunk.split("\n").drop(1).delete_if { |element| element.nil? || element.empty? }
    content.join("\n")
  end

  def self.parse_custodian(chunk)
    content = chunk.split("\n").drop(1).delete_if { |element| element.nil? || element.empty? }
    (content.select { |line| line =~ /^\* / })[0].tr('*', '').strip
  end

  def self.parse_approvals(chunk)
    status = 'draft'
    approvals = []
    date_regex = /\W?(\d?\d\/\d?\d\/\d\d\d\d)/
    content = chunk.split("\n").drop(1).delete_if { |element| element.nil? || element.empty? }
    content.each do |line|
      if line =~ /^\* /
        if line =~ /approval status:/i
          status_regex = /approval status:\s*(\w+)/i
          status_regex.match(line) do |m|
            if STATUS_TRANSLATE.include?(m[1].to_sym)
              status = STATUS_TRANSLATE[m[1].to_sym]
            else
              puts "******** Could not translate status: #{m[1]} *********"
            end
          end
        else
          work_group, temp_string = line.slice(2..-1).split(':')
          if temp_string =~ date_regex
            date_regex.match(temp_string) do |m|
              date = Date.strptime(m[1].strip, '%m/%d/%Y')
              approvals << [work_group, date]
              # puts '+++    found approval ' + work_group + ' on ' + date.to_s
            end
          else
            approvals << [work_group, temp_string]
            # puts '---    approval note ' + work_group + ' comment: ' + temp_string
          end
        end
      end
    end
    [status, approvals]
  end

  def self.parse_validation(chunk)
    validation_link = nil
    content = chunk.split("\n").drop(1).delete_if { |element| element.nil? || element.empty? }
    validation = (content.select { |line| line =~ /^\* /})
    if validation.size > 0
      site_line = validation[0].tr('*', '').strip
      link_regex = /\[site\]\((http(s)?:\/\/.*)\)/i
      link_regex.match(site_line) do |m|
        # puts " ~~~~~~~~~~~~~~~~~  found link: #{m[1]}  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        validation_link = m[1]
      end
    end
    validation_link
  end

  def self.parse_full_sample(chunk)
    content = chunk.split("\n").drop(1).delete_if { |element| element.nil? || element.empty? }
    (content.select { |line| line =~ /^\* /}).join(' ').tr('*', '')
  end

  def self.parse_keywords(chunk)
    content = chunk.split("\n").drop(1).delete_if { |element| element.nil? || element.empty? }
    (content.select { |line| line =~ /^\* /}).join(' ').tr('*,', '')
  end

  def self.parse_certifications(chunk)
    cert = false
    content = chunk.split("\n").drop(1).delete_if { |element| element.nil? || element.empty? }
    content.each { |line| cert = true if line =~ /(\Wonc)|(\Wonc\W)/i }
    cert
  end

  def self.parse_oids(chunk)
    nil
  end
end