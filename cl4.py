import os
import csv
import itertools
import sys
import re

def xor(a, b):
    """XOR operation"""
    return a != b

def parse_logical_expression(expr, variables):
    """Parse a logical expression and return a function to evaluate it"""
    # Clean the expression
    expr = expr.strip()
    original_expr = expr
    
    # Handle negation ¬ - be more careful with parentheses
    expr = re.sub(r'¬\(([^)]+)\)', r'(not (\1))', expr)
    expr = re.sub(r'¬([A-Z])', r'(not \1)', expr)
    
    # Handle XOR (⊕) - ensure proper spacing
    expr = re.sub(r'([A-Z])\s*⊕\s*([A-Z])', r'xor(\1, \2)', expr)
    
    # Handle biconditional (↔) - must be done before implication
    if '↔' in expr:
        parts = expr.split('↔')
        if len(parts) == 2:
            left = parts[0].strip()
            right = parts[1].strip()
            expr = f'({left}) == ({right})'
    
    # Handle implication (→)
    elif '→' in expr:
        parts = expr.split('→')
        if len(parts) == 2:
            left = parts[0].strip()
            right = parts[1].strip()
            expr = f'(not ({left})) or ({right})'
    
    # Handle logical operators
    expr = expr.replace('∧', ' and ')
    expr = expr.replace('∨', ' or ')
    
    print(f"Original: {original_expr}")
    print(f"Parsed: {expr}")
    
    # Create a function to evaluate the expression
    def evaluate(**kwargs):
        # Create local variables for evaluation
        local_vars = {}
        for var in variables:
            local_vars[var] = bool(kwargs.get(var, False))
        local_vars['xor'] = xor
        
        try:
            result = eval(expr, {"__builtins__": {}}, local_vars)
            return bool(result)
        except Exception as e:
            print(f"Error evaluating expression: {expr}")
            print(f"Variables: {local_vars}")
            print(f"Error details: {e}")
            return False
    
    return evaluate

def read_input_file(filename):
    """Read and parse the input file"""
    premises = []
    conclusion = None
    variables = set()
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Process each line
    for line in lines:
        line = line.strip()
        # Remove quotes if present
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        
        # Skip empty lines and certain keywords
        if not line or line.startswith('Variables:') or line == 'Premises:':
            continue
            
        # Find premises (numbered lines, including those starting with #)
        premise_match = re.match(r'#?(\d+)\)\s*(.+)', line)
        if premise_match:
            premise = premise_match.group(2).strip()
            # Only add premises that don't start with # (uncommented ones)
            if not line.startswith('#'):
                premises.append(premise)
                # Extract variables from premise
                vars_in_premise = re.findall(r'\b[A-Z]\b', premise)
                variables.update(vars_in_premise)
            continue
        
        # Find conclusion
        conclusion_match = re.match(r'Conclusion:\s*(.+)', line)
        if conclusion_match:
            conclusion = conclusion_match.group(1).strip()
            # Extract variables from conclusion
            vars_in_conclusion = re.findall(r'\b[A-Z]\b', conclusion)
            variables.update(vars_in_conclusion)
    
    return premises, conclusion, sorted(list(variables))

def generate_truth_table(input_filename):
    """Generate the truth table from input file"""
    # Check if input file exists
    if not os.path.exists(input_filename):
        print(f"Error: Input file '{input_filename}' not found.")
        return
    
    # Read and parse input file
    try:
        premises, conclusion, variables = read_input_file(input_filename)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return
    
    if not premises:
        print("No premises found in input file.")
        return
    
    if not conclusion:
        print("No conclusion found in input file.")
        return
    
    # Calculate statistics
    num_vars = len(variables)
    num_premises = len(premises)
    num_rows = 2 ** num_vars
    
    print(f"Found {num_premises} premises and 1 conclusion")
    print(f"Variables: {variables}")
    
    # Generate output filename
    base_name = os.path.splitext(input_filename)[0]
    output_filename = f"{base_name}.out.csv"
    
    # Create premise evaluators
    premise_evaluators = []
    for i, premise in enumerate(premises):
        try:
            evaluator = parse_logical_expression(premise, variables)
            premise_evaluators.append(evaluator)
            print(f"Premise {i+1}: {premise}")
        except Exception as e:
            print(f"Error parsing premise {i+1}: {premise}")
            print(f"Error: {e}")
            return
    
    # Create conclusion evaluator
    try:
        conclusion_evaluator = parse_logical_expression(conclusion, variables)
        print(f"Conclusion: {conclusion}")
    except Exception as e:
        print(f"Error parsing conclusion: {conclusion}")
        print(f"Error: {e}")
        return
    
    # Create headers - add index column first, then add numbers before each premise formula
    premise_cols = [f"{i+1}. {premise}" for i, premise in enumerate(premises)]
    header = ['Index'] + variables + premise_cols + ['All_Premises', conclusion, f'{conclusion} (Always)']
    
    # Generate all possible combinations
    rows = []
    
    for i, combination in enumerate(itertools.product([0, 1], repeat=num_vars), 1):
        # Create variable assignment
        var_dict = dict(zip(variables, combination))
        
        # Evaluate all premises
        premise_values = []
        for evaluator in premise_evaluators:
            try:
                result = evaluator(**var_dict)
                premise_values.append(int(result))
            except Exception as e:
                print(f"Error evaluating premise with {var_dict}: {e}")
                premise_values.append(0)
        
        # Check if all premises are true
        all_premises = all(premise_values)
        
        # Always evaluate conclusion for debugging
        try:
            conclusion_result = conclusion_evaluator(**var_dict)
            conclusion_value = int(conclusion_result)
        except Exception as e:
            print(f"Error evaluating conclusion with {var_dict}: {e}")
            conclusion_value = 0
        
        # For display, show conclusion value only when all premises are true
        if all_premises:
            conclusion_str = str(conclusion_value)
        else:
            conclusion_str = "-"
        
        # Create row - add index as first column, then variables, premises, etc.
        row = [i] + list(combination) + premise_values + [int(all_premises), conclusion_str, str(conclusion_value)]
        rows.append(row)
    
    # Determine if the argument is valid (conclusion is true in all rows where all premises are true)
    valid_rows = [row for row in rows if row[-3] == 1]  # All_Premises = 1 (now third from end)
    argument_valid = 1 if valid_rows and all(row[-2] == "1" for row in valid_rows) else 0
    
    # Count 0s and 1s for each variable when All_Premises=1
    var_counts_0 = {}
    var_counts_1 = {}
    
    for var in variables:
        var_index = variables.index(var) + 1  # +1 because of Index column
        if valid_rows:
            var_counts_0[var] = sum(1 for row in valid_rows if row[var_index] == 0)
            var_counts_1[var] = sum(1 for row in valid_rows if row[var_index] == 1)
        else:
            var_counts_0[var] = "-"
            var_counts_1[var] = "-"
    
    # Create the summary row showing argument validity
    summary_row = ["-"] + ["-"] * len(variables)  # Index + variable columns
    summary_row += ["-"] * len(premises)  # Fill premise columns with "-"
    summary_row += ["-"]  # All_Premises column
    summary_row += [str(argument_valid)]  # Argument validity (1 or 0)
    summary_row += [str(argument_valid)]  # Also add to the always-evaluated column
    
    # Create count rows for 0s and 1s
    count_0_row = ["0"] + ["-"] * len(variables)  # Index=0 + variable columns
    count_1_row = ["1"] + ["-"] * len(variables)  # Index=1 + variable columns
    
    # Fill in the counts for each variable
    for i, var in enumerate(variables):
        var_index = i + 1  # +1 because of Index column
        count_0_row[var_index] = str(var_counts_0[var])
        count_1_row[var_index] = str(var_counts_1[var])
    
    # Fill rest of count rows with "-"
    count_0_row += ["-"] * len(premises)  # Fill premise columns with "-"
    count_0_row += ["-"]  # All_Premises column
    count_0_row += ["-"]  # Conclusion columns
    count_0_row += ["-"]
    
    count_1_row += ["-"] * len(premises)  # Fill premise columns with "-"
    count_1_row += ["-"]  # All_Premises column
    count_1_row += ["-"]  # Conclusion columns
    count_1_row += ["-"]
    
    # Write to CSV file
    try:
        with open(output_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            writer.writerow(header)
            writer.writerows(rows)
            writer.writerow(summary_row)  # Add the summary row
            writer.writerow(count_0_row)  # Add count row for 0s
            writer.writerow(count_1_row)  # Add count row for 1s
            # Add statistics as individual rows at the end of CSV
            writer.writerow([f"# of variables: {num_vars}"])
            writer.writerow([f"# of Premises: {num_premises}"])
            writer.writerow([f"Number of rows in the truth table: {num_rows}"])
    except PermissionError:
        print(f"\nError: Cannot write to '{output_filename}' - file may be open in another program.")
        print("Please close the file in Excel/Notepad and try again, or delete the existing file.")
        
        # Try alternative filename
        counter = 1
        while True:
            try:
                base_name = os.path.splitext(input_filename)[0]
                alt_filename = f"{base_name}.out_{counter}.csv"
                with open(alt_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                    writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
                    writer.writerow(header)
                    writer.writerows(rows)
                    writer.writerow(summary_row)  # Add the summary row
                    writer.writerow(count_0_row)  # Add count row for 0s
                    writer.writerow(count_1_row)  # Add count row for 1s
                    # Add statistics as individual rows at the end of CSV
                    writer.writerow([f"# of variables: {num_vars}"])
                    writer.writerow([f"# of Premises: {num_premises}"])
                    writer.writerow([f"Number of rows in the truth table: {num_rows}"])
                output_filename = alt_filename
                print(f"Created alternative file: {output_filename}")
                break
            except PermissionError:
                counter += 1
                if counter > 10:
                    print("Cannot create output file. Please check file permissions.")
                    return
    
    print(f"\nTruth table generated and saved to: {output_filename}")
    
    # Print statistics immediately after the CSV file is written
    print(f"# of variables: {num_vars}")
    print(f"# of Premises: {num_premises}")
    print(f"Number of rows in the truth table: {num_rows}")
    
    # Print summary
    if valid_rows:
        print(f"\nRows where all premises are true: {len(valid_rows)}")
        print("Conclusion values for these rows:")
        for row in valid_rows:
            row_index = row[0]  # Get the actual index from the first column
            var_values = dict(zip(variables, row[1:num_vars+1]))  # Skip index column
            print(f"  Row {row_index}: {var_values} -> Conclusion: {row[-2]}")  # Use actual row index
        
        print(f"\nArgument validity: {argument_valid} ({'Valid' if argument_valid else 'Invalid'})")
    else:
        print("\nNo rows where all premises are true.")
        print(f"Argument validity: {argument_valid} (Invalid - no valid premise combinations)")

def test_expression():
    """Test function for debugging specific expressions"""
    # Test the specific case: (B⊕D)∧¬(C∧G) with B=1, C=0, D=0, G=0
    variables = ['B', 'C', 'D', 'G']
    expr = "(B⊕D)∧¬(C∧G)"
    
    evaluator = parse_logical_expression(expr, variables)
    
    # Test case from Row 2
    test_vars = {'B': 1, 'C': 0, 'D': 0, 'G': 0}
    result = evaluator(**test_vars)
    
    print(f"\nTest case:")
    print(f"Expression: {expr}")
    print(f"Variables: {test_vars}")
    print(f"Result: {result} ({int(result)})")
    
    # Manual calculation
    B, C, D, G = 1, 0, 0, 0
    xor_BD = B != D  # 1 != 0 = True
    and_CG = C and G  # 0 and 0 = False
    not_and_CG = not and_CG  # not False = True
    final = xor_BD and not_and_CG  # True and True = True
    
    print(f"\nManual calculation:")
    print(f"B⊕D = {B}⊕{D} = {xor_BD}")
    print(f"C∧G = {C}∧{G} = {and_CG}")
    print(f"¬(C∧G) = ¬{and_CG} = {not_and_CG}")
    print(f"(B⊕D)∧¬(C∧G) = {xor_BD}∧{not_and_CG} = {final}")

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) == 2 and sys.argv[1] == "test":
        test_expression()
        return
    
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_filename>")
        print("       python script.py test  (for testing)")
        print("Example: python script.py problem.txt")
        print("\nInput file format:")
        print("1) premise1")
        print("2) premise2")
        print("...")
        print("Conclusion: conclusion_expression")
        sys.exit(1)
    
    input_filename = sys.argv[1]
    generate_truth_table(input_filename)

if __name__ == "__main__":
    main()