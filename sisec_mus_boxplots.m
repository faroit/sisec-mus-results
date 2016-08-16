function sisec2015_mus_boxplots(varargin)

p = inputParser;
subsets_names = {'dev','test'};
sources_names = {'bass','drums','other','vocals','accompaniment'};
measures_names = {'sdr','isr','sir','sar'};
methods_names = { ...
    'OZE','DUR', ...
    'HUA', 'QIU'...
    'KAM1','KAM2', ...
    'STO1','STO2',...
    'NUG1','NUG3',...
    'RAF1','RAF2','RAF3', ...
    'UHL1','UHL2','UHL3' ...
    'YOU1','YOU2',...
    'GRA1','GRA2','GRA3',...
    'MIR',...
    'Ideal'};

addParameter(p,'subsets',subsets_names);
addParameter(p,'sources',sources_names);
addParameter(p,'measures',measures_names);
addParameter(p,'methods',methods_names);

parse(p,varargin{:});

subsets_names = lower(p.Results.subsets);
sources_names = lower(p.Results.sources);
measures_names = lower(p.Results.measures);
methods_names = p.Results.methods;

number_subsets = numel(subsets_names);
number_sources = numel(sources_names);
number_measures = numel(measures_names);
number_methods = numel(methods_names);
number_songs = 50;

%dataset_folder = fullfile(pwd,'resultsDSD');
dataset_folder ='/media/aliutkus/Reserved/ResultsDSD100/matfiles'

boxplots_limits = [+inf(number_measures,1),-inf(number_measures,1)];
for subset_index = 1:number_subsets
    for source_index = 1:number_sources
        for measure_index = 1:number_measures
            data_matrix = zeros(number_songs,number_methods);
            for method_index = 1:number_methods
                method_name = methods_names{method_index};
                method_file = fullfile(dataset_folder,[method_name,'.mat']);
                method_result = load(method_file);
                for song_index = 1:number_songs
                    method_values = method_result.result.(subsets_names{subset_index})(song_index).results.(sources_names{source_index}).(measures_names{measure_index});
                    if all(method_values==0 | isnan(method_values))
                        method_values = nan(size(method_values));
                    end
                    method_values(isnan(method_values)) = [];
                    data_matrix(song_index,method_index) = mean(method_values);
                end
            end
            w = 1.5;
            q1 = prctile(data_matrix,25,1);
            q3 = prctile(data_matrix,75,1);
            boxplots_limits(measure_index,1) = min(boxplots_limits(measure_index,1),min(q1-w*(q3-q1)));
            boxplots_limits(measure_index,2) = max(boxplots_limits(measure_index,2),max(q3+w*(q3-q1)));
        end
    end
end

font_size_median = 8;
font_size = 12;
close all

for source_index = 4:5%1:number_sources
    for subset_index = 1:2%1:number_subsets
    figure('Name',strcat(subsets_names{subset_index},sources_names{source_index}),'NumberTitle','off')
    set(gcf,'DefaultTextFontSize',font_size);
        for measure_index = 1:number_measures
            data_matrix = zeros(number_songs,number_methods);
            for method_index = 1:number_methods
                method_name = methods_names{method_index};
                method_file = fullfile(dataset_folder,[method_name,'.mat']);
                method_result = load(method_file);
                for song_index = 1:number_songs
                    method_values = method_result.result.(subsets_names{subset_index})(song_index).results.(sources_names{source_index}).(measures_names{measure_index});
                    if all(method_values==0 | isnan(method_values))
                        method_values = nan(size(method_values));
                    end
                    method_values(isnan(method_values)) = [];
                    data_matrix(song_index,method_index) = mean(method_values);
                end
            end
            %subplot(number_measures,2,(measure_index-1)*2+source_index-3)
            subplot(number_measures,1,measure_index)
            
            %subplot(number_measures,number_sources,(measure_index-1)*number_sources+source_index)
            boxplot(data_matrix,'labels',methods_names,'labelorientation','inline','notch','on','symbol','')
            if measure_index ~= number_measures 
                set(gca,'XTickLabel',{' '})
            end


            ylim(boxplots_limits(measure_index,:))
            grid on
            grid minor
            if measure_index == 1
                title(sources_names{source_index},'FontSize',font_size)
            end
            ylabel(upper(measures_names{measure_index}),'FontSize',font_size)
            v = axis; min_value=v(3);
            %min_value = prctile(data_matrix(:),05);
            for method_index = 1:number_methods
                median_value = median(data_matrix(:,method_index));
                
                prctile_value = min_value + abs(prctile(data_matrix(:,method_index),10)-min_value)*1/2;
                
                text(method_index,prctile_value,sprintf('%.1f',median_value), ...
                    'Color','r','HorizontalAlignment','Center','VerticalAlignment','Bottom','FontSize',font_size_median)
                
            end
            set(gca,'FontSize',font_size,'LineWidth',1)
        end
    end
end
