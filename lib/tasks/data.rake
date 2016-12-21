require 'rest-client'
require 'json'
require 'highline/import'
require 'base64'
require 'csv'

namespace :data do
  task :generate, [:date_val] => [:environment] do
    server = 'https://api.github.com/repos/HL7/C-CDA-Examples/'
    usr = ask('-->enter username: ') { |q| q.echo = '@'}
    pw = ask('-->enter password: ') { |q| q.echo = '@'}

    begin
      date = Date.today
      header = { Authorization: "Basic #{Base64.strict_encode64(usr + ':' + pw)}" }
      resp = RestClient.get "#{server}contents", header
      sections_csv = CSV.open(Rails.root + 'db/load-data/01-01-sections.csv', 'w')
      sect_no = 0
      sections_csv << %w(id name section_type narrative created_at updated_at)
      examples_csv = CSV.open(Rails.root + 'db/load-data/01-02-examples.csv', 'w')
      ex_no = 0
      examples_csv << %w(id section_id name comments custodian validation keywords onc_certification full_sample status oids example example_url created_at updated_at)
      approvals_csv = CSV.open(Rails.root + 'db/load-data/01-03-approvals.csv', 'w')
      approval_no = 0
      approvals_csv << %w(id example_id committee approved date comment)
      JSON.parse(resp).each do |entry|
        if entry['type'] == 'dir'
          sect_no += 1
          puts "#{sect_no}: #{entry['name']}"
          section_type = 'sect'
          narrative = nil
          dir_resp = RestClient.get entry['url'], header
          JSON.parse(dir_resp).each do |dir_entry|
            if dir_entry['type'] == 'dir'
              ex_no += 1
              metadata = ExampleMetadata.new
              example_contents = nil
              git_url = nil
              puts "   Found a directory named: #{dir_entry['name']}"
              ex_dir_resp = RestClient.get dir_entry['url'], header
              JSON.parse(ex_dir_resp).each do |ex_dir_entry|
                puts '          - ' + ex_dir_entry['type'] + '::' + ex_dir_entry['name']
                if ex_dir_entry['type'] == 'file'
                  if ex_dir_entry['name'] =~ /readme.md/i
                    metadata = MetadataParser.parse(RestClient.get(ex_dir_entry['download_url']))
                  elsif ex_dir_entry['name'] =~ /c(-)?cda2.1..xml/i
                    git_url = ex_dir_entry['html_url']
                    example_contents = RestClient.get ex_dir_entry['download_url']
                  end
                end
              end
              examples_csv << [ex_no, sect_no, dir_entry['name'], metadata[:comments],
                               metadata[:custodian], metadata[:validation],
                               metadata[:keywords], metadata[:onc_certification],
                               metadata[:full_sample], metadata[:status], metadata[:oids],
                               example_contents, git_url, date, date]
              if metadata.approvals
                metadata.approvals.each do |approval|
                  approval_no += 1
                  if approval[1].is_a?(Date)
                    approvals_csv << [approval_no, ex_no, approval[0], 't', approval[1], nil]
                  else
                    approvals_csv << [approval_no, ex_no, approval[0], 'f', nil, approval[1]]
                  end
                end
              end
            elsif dir_entry['type'] == 'file' && dir_entry['name'] =~ /readme.md/i
              # puts '   Found a ' + dir_entry['type'] + ' named ' + dir_entry['name']
              file_resp = RestClient.get dir_entry['download_url']
              narrative = file_resp
              if file_resp =~ /section examples/i
                section_type = 'sect'
              else
                section_type = 'doc'
              end
            end
          end
          sections_csv << [sect_no, entry['name'], section_type, narrative, date, date]
        end
      end
      sections_csv.close
      examples_csv.close
      approvals_csv.close
    rescue => e
      puts '****** FAILURE ******'
      puts e
      raise 'processing halted'
    end
  end
end
